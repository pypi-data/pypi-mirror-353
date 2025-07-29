# Databricks notebook source
from typing import Tuple, Union
from pyspark.sql.dataframe import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType
import json
import traceback
from datetime import datetime
import os
from smart_open import smart_open

from ETL.scripts.reported_issues.df_utils.df_utils import ReportedIssuesTable, db_name
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper, SchemaReport
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.commons.ease_of_use_fcns import filter_out_ingested_datasources
from ETL.logging.logging_decorators import log_general_info
from ETL.commons.reformat_data import (
    camel_to_snake_case, reformat_dict_data_field_types, none_empty_dict_fields, check_for_dict_data_expected_fields,
    uningested_fields
)

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/all_reported_issues.py"
etl_data = "reported_issues"
date_diff = -1 if datetime.now().hour < 3 else 0


def get_source_files(env):
    breadcrumbs = [
        "landing/reported_issues/calculation_error",
        "landing/reported_issues/input_error",
        "landing/reported_issues/mobile",
        "landing/reported_issues/other",
        "landing/reported_issues/technical_bug"
    ]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs=breadcrumbs, date_diff=date_diff)

    return file_helper


def read_json_file(file_path: str) -> dict:
    # Read json data from file
    f = smart_open(file_path, 'rb')
    json_data = json.load(f)
    f.close()

    return json.loads(json_data) if isinstance(json_data, str) else json.loads(json.dumps(json_data))


def preprocess_dict_data(dict_data: dict, table_schema: StructType) -> list:
    dict_list = [dict_data] if isinstance(dict_data, dict) else dict_data
    dict_list = [camel_to_snake_case(dict_list_el) for dict_list_el in dict_list]
    dict_list = [check_for_dict_data_expected_fields(dict_list_el, list(table_schema)) for dict_list_el in dict_list]
    dict_list = [reformat_dict_data_field_types(dict_list_el, list(table_schema)) for dict_list_el in dict_list]
    dict_list = [none_empty_dict_fields(dict_list_el) for dict_list_el in dict_list]

    return dict_list


def create_dataframe(spark: SparkSession, dict_list: list, table_schema: StructType) -> DataFrame:
    # Load data into spark dataframe along with the predefined schema
    return spark.createDataFrame(data=dict_list, schema=table_schema)


def etl_steps(spark: SparkSession, file_path: str, table_class, data_collected: dict) -> Tuple[list, dict]:
    # Read json data from file
    dict_data = read_json_file(file_path)
    print(f"\nProcessing data file for Table: {table_class.table_name}\n")
    print(f"data source: {file_path}\n")
    # Get table schema
    table_schema = table_class.get_spark_schema()
    # Preprocess the dict data
    dict_list = preprocess_dict_data(dict_data, table_schema)
    # Retrieve uningested fields
    missed_fields = uningested_fields(dict_list, table_schema)

    if table_class.table_name in list(data_collected.keys()):
        data_collected[table_class.table_name]["file_data"] += dict_list
    else:
        # Create table is not exist and insert dataframe into table
        spark.sql(table_class.create_table())
        new_data_collected = {
            table_class.table_name: {
                "file_data": dict_list,
                "table_schema": table_schema
            }
        }
        data_collected = {**data_collected, **new_data_collected}

    return missed_fields, data_collected


def write_files_to_tables(spark: SparkSession, files_contents: dict):
    for key, value in files_contents.items():
        table_schema = value["table_schema"]
        files_data = value["file_data"]

        # Create Spark DataFrame
        df = create_dataframe(spark, files_data, table_schema)
        df.write.insertInto(key, overwrite=False)


@log_general_info(
    env=locals(),
    etl_data=etl_data,
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    file_helper = get_source_files(env)
    # Instantiate table class
    table_class = ReportedIssuesTable()

    file_helper.file_paths, ingested_files_exceptions = filter_out_ingested_datasources(spark, file_helper.file_paths, etl_data)

    if not file_helper.file_paths:
        print(f"Exiting run:\n{file_helper.paths if not ingested_files_exceptions else ingested_files_exceptions}")
        return spark, [], file_helper.duration_s

    print(f"Spark UI Url: {spark_ui_url}")
    spark.sql(f"create database if not exists {db_name};")

    print(f"{len(file_helper.file_paths)} files to process")
    data_source_n_status = []
    data_collected = {}

    for file_path in file_helper.file_paths:
        logger_helper = LoggerHelper(source=file_path, path_n_sizes=file_helper.paths_n_sizes)
        try:
            missed_fields, data_collected = etl_steps(spark, file_path, table_class, data_collected)
            logger_helper.log_status(schema_report=SchemaReport(unexpected_fields=missed_fields))

            if file_path == file_helper.file_paths[-1]:
                print("Writing files data to tables...")
                write_files_to_tables(spark, data_collected)

        except Exception:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
