# Databricks notebook source
from typing import Union, Tuple

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
import json
import traceback
import xmltodict
import os
from smart_open import smart_open
import humps

from ETL.scripts.asset.df_utils.morningstar_xml_df_utils import *
from ETL.scripts.asset.views.morningstar_xml_views import views_sql
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper, SchemaReport
from ETL.commons.reformat_data import (
    reformat_dict_data_field_types, check_for_dict_data_expected_fields, add_file_arrival_date, add_file_path,
    none_empty_dict_fields
)
from ETL.commons.clean_data import clean_xmltodict_artifacts
from ETL.scripts.asset.normalization_utils.morningstar_xml_dataoutput_manual_normalization import (
    xml_dict_normalization, xml_isin_keys, xml_msid_keys
)
from ETL.commons.normalize_data import get_dict_key_paths
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/all_morningstar_xml.py"
etl_data_name = "asset_morningstar_xml"


def get_source_files(env):
    breadcrumbs = [
        "landing/asset/public_listed/morningstar/xml/isin/dataoutput",
        "landing/asset/public_listed/morningstar/xml/msid/dataoutput"
    ]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs, date_diff=-1)

    return file_helper


def read_xml_file(file_path: str) -> Union[dict, list]:
    f = smart_open(file_path, 'rb')
    try:
        xml_data = json.load(f)
    except:
        # the above works well but using this below for the sake of unittesting from temp memory files
        print("opening temp file from memory")
        f.seek(0)  # just to make sure the data is being read from the start of the file
        xml_data = f.read().decode("utf-8")
    f.close()
    # Convert XML string to JSON string
    xpars = xmltodict.parse(xml_data)
    json_data = json.dumps(xpars)

    return json.loads(json_data) if isinstance(json_data, str) else json.loads(json.dumps(json_data))


def get_filename_attr(file_path: str) -> Tuple[str, str, str, str, str]:
    file_isin = file_path.split("/")[-1].replace(".xml", "")

    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        file_arrival_date = "-".join(file_path.split("/")[-4:-1])
        file_tag = "_".join(file_path.split("/")[-5].lower().split("-"))
        sort_id = file_path.split("/")[-6]
    else:
        file_arrival_date = "-".join(file_path.split("/")[-2].split("_")[-3:])
        file_tag = file_path.split("/")[-2].split("_")[3].lower()
        sort_id = file_path.split("/")[-2].split("_")[2]

    class_name = humps.pascalize(file_tag) + f"{sort_id.upper()}Table"

    return file_isin, file_arrival_date, file_tag, sort_id, class_name


def check_for_uningested_fields(dict_data: dict, sort_id: str) -> list:
    file_key_paths = get_dict_key_paths(dict_data, False)
    expected_key_paths = xml_isin_keys() if sort_id == "isin" else xml_msid_keys()
    unexpected_key_paths = [key_path for key_path in file_key_paths if key_path not in expected_key_paths]

    def rm_stripped_down_keys(e_key_paths, u_key_paths):
        for u_key_path in u_key_paths:
            for i in range(1, len(u_key_path)-1):
                if u_key_path[:-i] in e_key_paths:
                    u_key_paths.remove(u_key_path)
                    u_key_paths = rm_stripped_down_keys(e_key_paths, u_key_paths)
                    break
        return u_key_paths

    return rm_stripped_down_keys(expected_key_paths, unexpected_key_paths)


def preprocess_dict_data(dict_data: Union[dict, list], file_path: str, file_arrival_date: str, sort_id: str, table_schema: StructType) -> Tuple[list, list]:
    """
    The following steps are performed in this function
    # Converted dict_data to a list if it isnt one already
    # Update dict_data with file_isin
    # Check for missing fields and assign None to missing fields
    # Reformat data to fit predefined schema datatypes
    """
    dict_data = clean_xmltodict_artifacts(dict_data)
    dict_parent_keys = list(dict_data.keys())
    if len(dict_parent_keys) == 1 and dict_parent_keys != ["FundShareClass"]:
        dict_data = dict_data[dict_parent_keys[0]]
    missed_fields = check_for_uningested_fields(dict_data, sort_id)
    dict_data = xml_dict_normalization(dict_data, sort_id)
    dict_data = add_file_path(dict_data, file_path)
    dict_data = add_file_arrival_date(dict_data, file_arrival_date)
    dict_data = check_for_dict_data_expected_fields(dict_data, table_schema)
    dict_data = reformat_dict_data_field_types(dict_data, table_schema)
    dict_data = none_empty_dict_fields(dict_data)

    return [dict_data] if isinstance(dict_data, dict) else dict_data, missed_fields


def create_dataframe(spark: SparkSession, dict_list: list, table_schema: StructType) -> DataFrame:
    # Load data into spark dataframe along with the predefined schema
    return spark.createDataFrame(data=dict_list, schema=table_schema)


def etl_steps(spark: SparkSession, file_path: str, data_collected: dict) -> Tuple[list, dict]:
    # Get file identifiers from filename
    file_isin, file_arrival_date, file_tag, sort_id, class_name = get_filename_attr(file_path)
    # Read json data from file
    dict_data = read_xml_file(file_path)
    # Instantiate table class
    table_class = eval(class_name + "()")
    print(f"\nProcessing data file for Table: {table_class.table_name}\n")
    print(f"data source: {file_path}\n")
    # Get table schema
    table_schema = table_class.get_spark_schema()
    # Preprocess the dict data
    dict_list, unexpected_key_paths = preprocess_dict_data(dict_data, file_path, file_arrival_date, sort_id,
                                                           table_schema)

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

    return unexpected_key_paths, data_collected


def write_files_to_tables(spark: SparkSession, files_contents: dict):
    for key, value in files_contents.items():
        table_schema = value["table_schema"]
        files_data = value["file_data"]

        batch_number = 1
        batch_increment = 100
        overwrite = True
        for indx in range(0, len(files_data), batch_increment):
            batch_data = files_data[indx:indx + batch_increment]
            # Create Spark DataFrame
            df = create_dataframe(spark, batch_data, table_schema)
            df.write.insertInto(key, overwrite=overwrite)
            print(f"batch write: {batch_number} | wrote into {key} with overwrite={overwrite}")
            batch_number += 1
            overwrite = False


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

    for view_sql in views_sql:
        logger_helper = LoggerHelper(source=view_sql)
        try:
            spark.sql(view_sql)
            logger_helper.log_status()
        except Exception as e:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
