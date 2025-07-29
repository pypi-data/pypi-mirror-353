# Databricks notebook source
import traceback
from typing import Tuple

import os
from pyspark.sql.dataframe import DataFrame, SparkContext
from pyspark.sql import SparkSession
import smart_open

from ETL.scripts.ms_integration.source_data_mapper import *
from ETL.commons.clean_data import clean_csv_col_names
from ETL.commons.reformat_data import reformat_df_data_field_types
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/all_ms_integration_csv_txt.py"
etl_data_name = "ms_integration_csv_txt"


def get_source_files(env):
    breadcrumbs = [
        "landing/financial_statement/ms-integration/brooks_mcdonald",
        "landing/financial_statement/ms-integration/canaccord",
        "landing/financial_statement/ms-integration/cazenove_capital",
        "landing/financial_statement/ms-integration/charles_stanley",
        "landing/financial_statement/ms-integration/citi",
        "landing/financial_statement/ms-integration/citi_jersey",
        "landing/financial_statement/ms-integration/citi_singapore",
        "landing/financial_statement/ms-integration/credit_suisse",
        "landing/financial_statement/ms-integration/credo",
        "landing/financial_statement/ms-integration/goldman_sachs",
        "landing/financial_statement/ms-integration/hedgeserv",
        "landing/financial_statement/ms-integration/interactive_brokers",
        "landing/financial_statement/ms-integration/investec",
        "landing/financial_statement/ms-integration/jp_morgan",
        "landing/financial_statement/ms-integration/julius_baer",
        "landing/financial_statement/ms-integration/killik",
        "landing/financial_statement/ms-integration/kleinwort_hambros",
        "landing/financial_statement/ms-integration/lombard_international_assurance",
        "landing/financial_statement/ms-integration/lombard_odier",
        "landing/financial_statement/ms-integration/morgan_stanley",
        "landing/financial_statement/ms-integration/pictet",
        "landing/financial_statement/ms-integration/rbc",
        "landing/financial_statement/ms-integration/rbc_us",
        "landing/financial_statement/ms-integration/rothschild",
        "landing/financial_statement/ms-integration/ruffer",
        "landing/financial_statement/ms-integration/ubs",
    ]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs=breadcrumbs)
    file_helper.file_paths = [el for el in file_helper.file_paths if el.split(".")[-1] not in ["xml"]]

    return file_helper


def read_csv_file(file_path: str) -> list:
    f = smart_open.open(file_path, 'rb', encoding='utf-8', errors='ignore')
    csv_data = f.readlines()
    f.close()
    return csv_data


def get_filename_attr(file_path: str) -> Tuple[str, str]:
    file_name = file_path.split("/")[-1]
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        data_name = file_path.split("/")[-4]
        file_arrival_date_str = file_path.split("/")[-2]
    else:
        file_arrival_date_str = file_path.split("/")[-2].split("_")[-1]
        data_name = file_path.split("/")[-2]\
            .replace(f"_{file_arrival_date_str}", "")\
            .replace("_testfiles", "")\
            .replace("_prepared", "")\
            .replace("_wealth", "")

    return file_name, data_name


def add_csv_header(csv_data: list, table_class):
    if table_class.column_line:
        has_header = clean_csv_col_names(table_class.column_line[0], table_class.sep) ==\
                     clean_csv_col_names(csv_data[0], table_class.sep)

        csv_data = table_class.column_line + csv_data if not has_header else csv_data

    return csv_data


def create_dataframe(spark: SparkSession, sc: SparkContext, csv_data: list, sep: str) -> DataFrame:
    # Load data into spark dataframe along with the predefined schema
    csv_rdd = sc.parallelize(csv_data)
    return spark.read.option("header", True).option("delimiter", sep).option("inferSchema", False).csv(csv_rdd)


def etl_steps(spark: SparkSession, sc: SparkContext, file_path: str):
    # Get file identifiers from filename
    file_name, data_name = get_filename_attr(file_path)
    # Read csv data from file
    csv_data = read_csv_file(file_path)
    if not csv_data:
        return []
    # Instantiate table class
    table_class = source_data_class_mapper(data_name, file_name)
    col_index = table_class.column_line_index
    # Add csv header
    csv_data[col_index:] = add_csv_header(csv_data[col_index:], table_class)
    # Rename table columns
    csv_data[col_index] = clean_csv_col_names(csv_data[col_index], table_class.sep)
    print(f"\nProcessing data file for Table: {table_class.table_name}\n")
    print(f"data source: {file_path}\n")
    # Create Spark DataFrame
    df = create_dataframe(spark, sc, csv_data[col_index:], table_class.sep)
    # Reformat the df to cast the fields with the expected datatype as stated in the table spark schema
    df, schema_report = reformat_df_data_field_types(df, table_class)
    # Create table is not exist and insert dataframe into table
    spark.sql(table_class.create_table())
    df.write.insertInto(table_class.table_name, overwrite=True)

    return schema_report


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict):
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
            schema_report = etl_steps(spark, sc, file_path)
            logger_helper.log_status(schema_report=schema_report)

        except Exception:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
