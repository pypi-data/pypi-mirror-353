# Databricks notebook source
from typing import Union, Tuple

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
import json
import traceback
import os
from smart_open import smart_open
import humps

from ETL.scripts.asset.df_utils.reuters_json_df_utils import *
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper, remove_logged_processed_files, \
    SchemaReport
from ETL.commons.reformat_data import (
    reformat_dict_data_field_types, check_for_dict_data_expected_fields, add_file_arrival_date, add_file_path,
    add_file_id, none_empty_dict_fields, clean_dict_field_names, uningested_fields
)
from ETL.commons.normalize_data import normalize_dict_with_pd
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/all_reuters_json.py"
etl_data_name = "asset_reuters_json"


def get_source_files(env):
    breadcrumbs = [
        "landing/asset/public_listed/reuters/json/composite",
        "landing/asset/public_listed/reuters/json/fund-allocation",
        "landing/asset/public_listed/reuters/json/price-history",
        "landing/asset/public_listed/reuters/json/term-and-conditions",
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


def read_json_file(file_path: str) -> Union[dict, list]:
    f = smart_open(file_path, 'rb')
    # json.loads(json.load(f))
    # The above works well but the implementation below is to allow for unittesting this function with temp file
    json_data = json.load(f)
    f.close()

    return json.loads(json_data) if isinstance(json_data, str) else json.loads(json.dumps(json_data))


def get_filename_attr(file_path: str) -> Tuple[str, str, str, str]:
    file_id = file_path.split("/")[-1].replace(".json", "")

    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        file_arrival_date = "-".join(file_path.split("/")[-4:-1])
        file_tag = "_".join(file_path.split("/")[-5].lower().split("-"))
    else:
        file_arrival_date = "-".join(file_path.split("/")[-2].split("_")[-3:])
        file_tag = "_".join(file_path.split("/")[-2].split("_")[2].lower().split("-"))

    class_name = humps.pascalize(file_tag) + "Table"

    return file_id, file_arrival_date, file_tag, class_name


def preprocess_dict_data(dict_data: Union[dict, list], file_path: str, file_arrival_date: str, file_id: str, table_schema: StructType) -> list:
    """
    The following steps are performed in this function
    # Converted dict_data to a list if it isnt one already
    # Update dict_data with file_isin
    # Check for missing fields and assign None to missing fields
    # Reformat data to fit predefined schema datatypes
    """
    dict_list = [dict_data] if isinstance(dict_data, dict) else dict_data
    dict_list = normalize_dict_with_pd(dict_list)
    dict_list = [clean_dict_field_names(dict_list_el, rm_prefix="contents_") for dict_list_el in dict_list]
    dict_list = [add_file_id(dict_list_el, file_id) for dict_list_el in dict_list]
    dict_list = [add_file_path(dict_list_el, file_path) for dict_list_el in dict_list]
    dict_list = [add_file_arrival_date(dict_list_el, file_arrival_date) for dict_list_el in dict_list]
    dict_list = [check_for_dict_data_expected_fields(dict_list_el, table_schema) for dict_list_el in dict_list]
    dict_list = [reformat_dict_data_field_types(dict_list_el, table_schema) for dict_list_el in dict_list]
    dict_list = [none_empty_dict_fields(dict_list_el) for dict_list_el in dict_list]

    return dict_list


def create_dataframe(spark: SparkSession, dict_list: list, table_schema: StructType) -> DataFrame:
    # Load data into spark dataframe along with the predefined schema
    return spark.createDataFrame(data=dict_list, schema=table_schema)


def etl_steps(spark: SparkSession, file_path: str, overwrite_mode: bool) -> list:
    # Get file identifiers from filename
    file_id, file_arrival_date, file_tag, class_name = get_filename_attr(file_path)
    # Read json data from file
    dict_data = read_json_file(file_path)
    # Instantiate table class
    table_class = eval(class_name + "()")
    print(f"\nProcessing data file for Table: {table_class.table_name}\n")
    print(f"data source: {file_path}\n")
    # Get table schema
    table_schema = table_class.get_spark_schema()
    # Preprocess the dict data
    dict_list = preprocess_dict_data(dict_data, file_path, file_arrival_date, file_id, table_schema)
    # Retrieve uningested fields
    missed_fields = uningested_fields(dict_list, table_schema)
    write_files_to_tables(spark, dict_list, table_class, overwrite_mode=overwrite_mode)

    return missed_fields


def write_files_to_tables(spark: SparkSession, file_data: list, table_class, overwrite_mode: bool):
    spark.sql(table_class.create_table())
    table_schema = table_class.get_spark_schema()
    table_name = table_class.table_name

    batch_number = 1
    batch_increment = 20000

    print(f"\nWriting {table_name} data in batches...")
    for indx in range(0, len(file_data), batch_increment):
        batch_data = file_data[indx:indx + batch_increment]
        end_indx = indx + batch_increment if indx + batch_increment < len(file_data) else len(file_data)
        # Create Spark DataFrame
        df = create_dataframe(spark, batch_data, table_schema)
        df.write.insertInto(table_name, overwrite=overwrite_mode)
        print(
            f"Wrote {indx}:{end_indx} data range of {len(file_data)} into {table_name} with {'overwrite' if overwrite_mode else 'append'} mode")

        batch_number += 1


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
        file_helper.file_paths = remove_logged_processed_files(spark, etl_data_name, file_helper.file_paths, batch=False)

    if not file_helper.file_paths:
        print("Exiting run:\n"+"\n".join(file_helper.get_s3_files_exceptions))
        return spark, [], file_helper.duration_s

    print(f"Spark UI Url: {spark_ui_url}")
    spark.sql(f"create database if not exists {db_name};")

    print(f"{len(file_helper.file_paths)} files to process")
    data_source_n_status = []
    file_partitions = partition_files(file_helper.file_paths)

    for event_key, file_paths in file_partitions.items():
        overwrite_mode = True
        for file_path in file_paths:
            logger_helper = LoggerHelper(source=file_path, path_n_sizes=file_helper.paths_n_sizes)
            try:
                missed_fields = etl_steps(spark, file_path, overwrite_mode)
                overwrite_mode = False
                logger_helper.log_status(schema_report=SchemaReport(unexpected_fields=missed_fields))
            except Exception as e:
                logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

            data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
