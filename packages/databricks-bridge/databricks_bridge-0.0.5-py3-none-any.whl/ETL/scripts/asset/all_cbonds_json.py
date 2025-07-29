# Databricks notebook source
import traceback
import os
from typing import Tuple

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.dataframe import DataFrame

from ETL.scripts.asset.df_utils.cbonds_df_utils import *
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/all_cbonds_json.py"
etl_data_name = "asset_cbonds_json"


def get_source_files(env):
    breadcrumbs = [
        "landing/asset/public_listed/cbonds/json/emission",
        "landing/asset/public_listed/cbonds/json/flows",
        "landing/asset/public_listed/cbonds/json/tradings"
    ]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs, date_diff=-1)

    return file_helper


def partition_files(file_paths: list):
    files_partitions = {}
    for path in file_paths:
        event = path.split("/")[-5]
        if event in files_partitions.keys():
            files_partitions[event].append(path)
        else:
            files_partitions[event] = [path]

    return files_partitions


def get_table_class(event_key):
    if event_key == "emission":
        return EmissionTable()
    elif event_key == "flows":
        return FlowsTable()
    elif event_key == "tradings":
        return TradingsTable()
    else:
        raise KeyError(f"Unexpected Event Key: {event_key}")


def add_file_isin(df: DataFrame) -> DataFrame:
    if "isin_code" not in df.columns:
        df = df.withColumn("file_path_split", F.split(F.col("file_path"), "/")) \
            .withColumn("file_isin", F.col("file_path_split").getItem(F.size(F.col("file_path_split")) - 1)) \
            .withColumn("file_isin", F.regexp_replace("file_isin", ".json", ""))\
            .drop(*["file_path_split"])

    return df


def add_file_arrival_date(df: DataFrame) -> DataFrame:
    df = df.withColumn("file_path_split", F.split(F.col("file_path"), "/")) \
        .withColumn("_day", F.col("file_path_split").getItem(F.size(F.col("file_path_split")) - 2)) \
        .withColumn("_month", F.col("file_path_split").getItem(F.size(F.col("file_path_split")) - 3)) \
        .withColumn("_year", F.col("file_path_split").getItem(F.size(F.col("file_path_split")) - 4)) \
        .withColumn("file_arrival_date", F.concat_ws("-", F.col("_year"), F.col("_month"), F.col("_day"))) \
        .drop(*["_year", "_month", "_day", "file_path_split"])

    return df


def create_json_dataframe(spark: SparkSession, file_paths: list) -> DataFrame:
    # Load data into spark dataframe
    return spark.read.json(file_paths).withColumn("file_path", F.input_file_name())


def etl_steps(spark: SparkSession, file_paths: list, table_class, overwrite_mode: bool) -> list:
    df = create_json_dataframe(spark, file_paths)
    df.cache()
    df = add_file_isin(df)
    df = add_file_arrival_date(df)
    df, schema_report = reformat_df_data_field_types2(df, table_class)
    write_df_to_tables(spark, df, table_class, overwrite_mode)

    return schema_report


def write_df_to_tables(spark: SparkSession, df: DataFrame, table_class, overwrite_mode: bool = False):
    spark.sql(table_class.create_table())
    table_schema = table_class.get_spark_schema()
    col_names = table_schema.names
    df.select(col_names).write.insertInto(table_class.table_name, overwrite=overwrite_mode)


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    file_helper = get_source_files(env)
    if not file_helper.file_paths:
        print("Exiting run:\n" + "\n".join(file_helper.get_s3_files_exceptions))
        return spark, [], file_helper.duration_s

    spark, sc, spark_ui_url = get_or_create_spark_session(env)

    print(f"Spark UI Url: {spark_ui_url}")
    spark.sql(f"create database if not exists {db_name};")

    print(f"{len(file_helper.file_paths)} files to process")
    data_source_n_status = []
    file_partitions = partition_files(file_helper.file_paths)

    for event_key, file_paths in file_partitions.items():
        batch_number = 1
        batch_increment = 1000
        overwrite_mode = True

        for indx in range(0, len(file_paths), batch_increment):
            batch_paths = file_paths[indx:indx + batch_increment]
            logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
            table_class = get_table_class(event_key)
            class_name = table_class.__class__.__name__

            try:
                print(f"Batch {batch_number} - Reading {class_name} data files data to memory...")
                schema_report = etl_steps(spark, batch_paths, table_class, overwrite_mode)
                end_indx = indx + batch_increment if indx + batch_increment < len(file_paths) else len(file_paths)
                print(
                    f"Wrote {indx}:{end_indx} data range of {len(file_paths)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")

                batch_number += 1
                overwrite_mode = False

                logger_helper.log_status(schema_report=schema_report)

            except Exception as e:
                msg = f"Error on {class_name} data\n{traceback.format_exc()}"
                logger_helper.log_status(traceback=msg, failed=True)
                print(logger_helper.source_n_status["traceback"])

            data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
