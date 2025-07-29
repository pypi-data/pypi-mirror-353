# Databricks notebook source
from typing import Union, Tuple

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import StructType
import json
import traceback
import xmltodict
import sys
import os
from smart_open import smart_open

from ETL.scripts.ms_integration.source_data_mapper import *
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper, SchemaReport
from ETL.commons.reformat_data import (
    reformat_dict_data_field_types, check_for_dict_data_expected_fields, uningested_fields, none_empty_dict_fields
)
from ETL.commons.clean_data import clean_xmltodict_artifacts
from ETL.commons.normalize_data import normalize_dict_with_pd
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/all_ms_integration_xml.py"
etl_data_name = "ms_integration_xml"


def get_source_files(env):
    breadcrumbs = [
        "landing/financial_statement/ms-integration/handelsbanken",
        "landing/financial_statement/ms-integration/credit_suisse"
    ]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs=breadcrumbs)
    file_helper.file_paths = [el for el in file_helper.file_paths if el.split(".")[-1] == "xml"]

    return file_helper


def read_xml_file(file_path: str) -> Union[dict, list]:
    f = smart_open(file_path, 'rb')
    xml_data = f.read().decode("utf-8")
    f.close()
    # Convert XML string to JSON string
    xpars = xmltodict.parse(xml_data)
    json_data = json.dumps(xpars)

    return json.loads(json_data) if isinstance(json_data, str) else json.loads(json.dumps(json_data))


def get_filename_attr(file_path: str) -> Tuple[str, str]:
    file_name = file_path.split("/")[-1]
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        data_name = file_path.split("/")[-4]
        file_arrival_date_str = file_path.split("/")[-2]
    else:
        file_arrival_date_str = file_path.split("/")[-2].split("_")[-1]
        data_name = file_path.split("/")[-2] \
            .replace(f"_{file_arrival_date_str}", "") \
            .replace("_testfiles", "")

    return file_name, data_name


def preprocess_dict_data(dict_data: dict, table_schema: StructType) -> list:
    dict_data = clean_xmltodict_artifacts(dict_data)
    dict_list = normalize_dict_with_pd(dict_data)
    dict_list = [check_for_dict_data_expected_fields(dict_list_el, list(table_schema)) for dict_list_el in dict_list]
    dict_list = [reformat_dict_data_field_types(dict_list_el, list(table_schema)) for dict_list_el in dict_list]
    dict_list = [none_empty_dict_fields(dict_list_el) for dict_list_el in dict_list]

    return dict_list


def create_dataframe(spark: SparkSession, dict_list: list, table_schema: StructType) -> DataFrame:
    # Load data into spark dataframe along with the predefined schema
    return spark.createDataFrame(data=dict_list, schema=table_schema)


def etl_steps(spark: SparkSession, file_path: str, data_collected: dict) -> Tuple[list, dict]:
    # Get file identifiers from filename
    file_name, data_name = get_filename_attr(file_path)
    # Read json data from file
    dict_data = read_xml_file(file_path)
    # Instantiate table class
    table_class = source_data_class_mapper(data_name, file_name)
    print(f"\nProcessing data file for Table: {table_class.table_name}\n")
    print(f"data source: {file_path}\n")
    dict_data_roi = table_class.get_dict_roi(dict_data)
    # Get table schema
    table_schema = table_class.get_spark_schema()
    # Preprocess the dict data
    dict_list = preprocess_dict_data(dict_data_roi, table_schema)
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
        df.write.insertInto(key, overwrite=True)


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
        print("Exiting run:\n"+"\n".join(file_helper.get_s3_files_exceptions))
        return spark, [], file_helper.duration_s

    print(f"Spark UI Url: {spark_ui_url}")
    spark.sql(f"create database if not exists {db_name};")

    print(f"{len(file_helper.file_paths)} files to process")
    data_source_n_status = []
    data_collected = {}

    for file_path in file_helper.file_paths:
        logger_helper = LoggerHelper(source=file_path, path_n_sizes=file_helper.paths_n_sizes)
        try:
            missed_fields, data_collected = etl_steps(spark, file_path, data_collected)
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
