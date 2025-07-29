# Databricks notebook source
from typing import Tuple
import os
import humps
import traceback

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from ETL.scripts.ms_pod_hub.df_utils.task_data_df_utils import *
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/task_data_etl.py"
table_class = TaskDataTable()


def get_source_files(env):
    breadcrumbs = ["landing/ms-pod-hub/TaskEvent"]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs, date_diff=-1)

    return file_helper


def remove_processed_files(spark: SparkSession, file_paths: list) -> list:
    query = table_class.unprocessed_files_filter_query(etl_data_name, file_paths)
    try:
        data_source_rdd = spark.sql(query).collect()
    except Exception as e:
        data_source_rdd = []
        print(e)

    if len(data_source_rdd) == 0:
        return file_paths
    else:
        processed_files = [row.data_source for row in data_source_rdd]
        unprocessed_files = [path for path in file_paths if path not in processed_files]
        print(f"{len(processed_files)}/{len(file_paths)} were already processed successfully so they have been removed")
        return unprocessed_files


def create_json_dataframe(spark: SparkSession, file_paths: list) -> DataFrame:
    # Load data into spark dataframe
    return spark.read.json(file_paths, multiLine=True)


def rename_df_cols(df: DataFrame) -> DataFrame:
    renamed_cols = [f"{_col} as {humps.decamelize(_col)}" for _col in df.columns]
    df = df.selectExpr(renamed_cols)
    return df


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str):
    df.select(col_names).write.insertInto(table_name, overwrite=False)


def etl_steps(spark: SparkSession, file_path: list) -> list:
    df = create_json_dataframe(spark, file_path)
    df = rename_df_cols(df)
    df_final, schema_report = reformat_df_data_field_types2(df, table_class)
    spark.sql(table_class.create_table())
    table_schema = table_class.get_spark_schema()
    task_ids = [row.id for row in df_final.select("id").collect()]
    spark.sql(table_class.delete_table_rows(task_ids))
    write_files_to_tables(df_final, table_schema.names, table_class.table_name)

    return schema_report


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")
    file_helper = get_source_files(env)
    class_name = "TaskDataTable"
    if file_helper.file_paths:
        file_paths = remove_processed_files(spark, file_helper.file_paths)

    if not file_helper.file_paths:
        print("Exiting run:\n" + "\n".join(file_helper.get_s3_files_exceptions))
        return spark, [], file_helper.duration_s

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
            schema_report = etl_steps(spark, batch_paths)
            end_indx = indx + batch_increment if indx + batch_increment < len(file_helper.file_paths) else len(file_helper.file_paths)
            print(
                f"Wrote {indx}:{end_indx} data range of {len(file_helper.file_paths)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")

            batch_number += 1
            logger_helper.log_status(schema_report=schema_report)

        except Exception as e:
            msg = f"Error on {class_name} data\n{traceback.format_exc()}"
            logger_helper.log_status(traceback=msg, failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
