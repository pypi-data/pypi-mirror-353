# Databricks notebook source
from typing import Tuple, Union
from pyspark.sql.dataframe import DataFrame, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as f
import traceback
import os

from ETL.scripts.ms_integration.df_utils.relationship_issues_df_utils import RelationshipIssuesTable, db_name, etl_data_name
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.normalize_data import decamelize_df_cols
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper, remove_logged_processed_files
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/relationship_issues_etl.py"
table_class = RelationshipIssuesTable()
table_schema = table_class.get_spark_schema()
class_name = table_class.__class__.__name__


def get_source_files(env):
    breadcrumbs = ["landing/financial_statement/relationship-issues/json/no-relationship"]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs=breadcrumbs)

    return file_helper


def create_json_dataframe(spark: SparkSession, file_paths: list) -> DataFrame:
    # Load data into spark dataframe
    return spark.read.json(file_paths)


def write_df_to_table(df: DataFrame, col_names: list, table_name: str, overwrite: bool = False):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite)


def extract_relationship_status(df: DataFrame):
    df = df.withColumn("file_path", f.input_file_name()) if "file_path" not in df.columns else df
    df = df.withColumn("relationship_status", f.split(f.col("file_path"), "/").getItem(7)).drop("file_path")
    return df


def etl_steps(spark: SparkSession, file_paths: list, overwrite: bool):
    df = create_json_dataframe(spark, file_paths)
    df = decamelize_df_cols(df)
    df = extract_relationship_status(df)
    df = df.withColumn("insert_timestamp", f.expr("current_timestamp()"))
    df, schema_report = reformat_df_data_field_types2(df, table_class)
    spark.sql(table_class.create_table())
    write_df_to_table(df, table_schema.names, table_class.table_name, overwrite)
    return schema_report


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    file_helper = get_source_files(env)
    if file_helper.file_paths:
        file_helper.file_paths = remove_logged_processed_files(spark, etl_data_name, file_helper.file_paths, batch=True)

    if not file_helper.file_paths:
        print("Exiting run:\n" + "\n".join(file_helper.get_s3_files_exceptions))
        return spark, [], file_helper.duration_s

    print(f"Spark UI Url: {spark_ui_url}")
    spark.sql(f"create database if not exists {db_name};")

    print(f"{len(file_helper.file_paths)} files to process")
    data_source_n_status = []

    batch_number = 1
    batch_increment = 1000
    overwrite_mode = False

    for indx in range(0, len(file_helper.file_paths), batch_increment):
        batch_paths = file_helper.file_paths[indx:indx + batch_increment]
        logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
        try:
            print(f"Batch {batch_number} - Reading {class_name} data files data to memory...")
            schema_report = etl_steps(spark, batch_paths, overwrite_mode)
            end_indx = indx + batch_increment if indx + batch_increment < len(file_helper.file_paths) else len(file_helper.file_paths)
            print(
                f"Wrote {indx}:{end_indx} data range of {len(file_helper.file_paths)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")

            batch_number += 1
            logger_helper.log_status(schema_report=schema_report)
            overwrite_mode = False

        except Exception as e:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)
            print(traceback.format_exc())

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
