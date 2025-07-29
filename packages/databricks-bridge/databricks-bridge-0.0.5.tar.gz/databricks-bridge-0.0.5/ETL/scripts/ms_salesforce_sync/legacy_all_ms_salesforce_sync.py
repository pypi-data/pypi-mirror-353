# Databricks notebook source
from typing import Tuple, Union

import humps
import os
import traceback
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame

from ETL.scripts.ms_salesforce_sync.df_utils.legacy_ms_salesforce_sync_df_utils import *
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/legacy_all_ms_salesforce_sync.py"


def get_source_files(env):
    breadcrumbs = ["landing/salesforce/ms-salesforce-sync"]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs, date_diff=-1)
    if file_helper.file_paths:
        file_helper.file_paths = [path for path in file_helper.file_paths if path[-8:] != "_all.csv"]

    return file_helper


def create_dataframe(spark: SparkSession, file_path: str, table_schema: StructType) -> DataFrame:
    # Load data into spark dataframe along with the predefined schema
    return spark.read.format("csv").option("header", True).option("multiline", True).schema(table_schema).load(file_path)


def get_filename_attr(file_path: str) -> Tuple[str, str]:
    file_tag = file_path.split("/")[-1].replace(".csv", "").lower()
    class_name = humps.pascalize(file_tag) + "Table"

    return file_tag, class_name


def etl_steps(spark: SparkSession, file_path: str):
    # Get file identifiers from filename
    file_tag, class_name = get_filename_attr(file_path)
    # Instantiate table class
    table_class = eval(f"{class_name}()")
    print(f"\nProcessing data file for Table: {table_class.table_name}\n")
    print(f"data source: {file_path}\n")
    # Get table schema
    table_schema = table_class.get_spark_schema()
    # Create Spark DataFrame
    df = create_dataframe(spark, file_path, table_schema)
    # Create table is not exist and insert dataframe into table
    spark.sql(table_class.create_table())
    df.write.insertInto(table_class.table_name, overwrite=True)


@log_general_info(
    env=locals(),
    etl_data="ms_salesforce_sync",
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    file_helper = get_source_files(env)

    if not file_helper.file_paths:
        print(f"Exiting run:\n{file_helper.paths}")
        return spark, [], file_helper.duration_s

    print(f"Spark UI Url: {spark_ui_url}")
    spark.sql(f"create database if not exists {db_name};")

    print(f"{len(file_helper.file_paths)} files to process")
    data_source_n_status = []

    for file_path in file_helper.file_paths:
        logger_helper = LoggerHelper(source=file_path, path_n_sizes=file_helper.paths_n_sizes)
        try:
            etl_steps(spark, file_path)
            logger_helper.log_status()
        except Exception:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
