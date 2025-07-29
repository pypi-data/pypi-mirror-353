# Databricks notebook source
from typing import Union, Tuple, List, Dict
import os
import json
import humps
import traceback

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame, SparkContext
from pyspark.sql.functions import explode

from ETL.scripts.hubspot.df_utils.hubspot_df_utils import *

from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import read_json_file
from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.decrypt_encrypt_data import ms_datalake_connector_decryption
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/hubspot_etl.py"


def get_source_files(env):
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs="landing/hubspot")

    return file_helper


def remove_processed_files(spark: SparkSession, file_paths: list, query: str) -> list:

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


def retrieve_table_class(file_path: str, just_class_name: bool = False):
    file_name = file_path.split("/")[-1]
    class_name = humps.pascalize("_".join([el for el in file_name.split("-")[0].split("_") if not el.isdigit()])) + "Table"
    if just_class_name:
        return class_name, None

    table_class = eval(f"{class_name}()")
    return class_name, table_class


def read_encrypted_file(env: dict, file_path: str) -> Union[List, Dict]:
    stripped_path = "/".join(file_path.split("/")[3:])
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        status_code, file_content = ms_datalake_connector_decryption(env, stripped_path)
        data = json.loads(file_content) if status_code == 200 else None
    else:
        data = read_json_file(file_path)

    return data


def restructure_page_data_dict(dict_data: dict):
    dict_list = []
    for key, val in dict_data.items():
        if isinstance(val, list):
            for i in range(len(val)):
                val[i]["date"] = key
        dict_list = dict_list + val

    return dict_list


def explode_df(df: DataFrame, table_class) -> DataFrame:
    array_col = table_class.explodable_column
    if array_col in df.columns:
        df_array_explode = df.select("*", explode(df[array_col]).alias(f"{array_col}_exploded")).drop(array_col)
        df_struct_explode = df_array_explode.select("*", f"{array_col}_exploded.*").drop(f"{array_col}_exploded")
    else:
        df_struct_explode = df

    df_struct_explode = rename_df_cols(df_struct_explode)

    return df_struct_explode


def explode_breakdowns_df(df: DataFrame) -> DataFrame:
    array_col = "breakdowns"
    if array_col in df.columns:
        df_array_explode = df.select("*", explode(df[array_col]).alias(f"{array_col}_exploded")).drop(array_col)
        df_array_explode = df_array_explode.withColumnRenamed(f"{array_col}_exploded", array_col)
    else:
        return df

    return df_array_explode


def create_json_dataframe(spark: SparkSession, sc: SparkContext, dict_list: list) -> DataFrame:
    # Load data into spark dataframe
    return spark.read.json(sc.parallelize([json.dumps(dict_list)]))


def rename_df_cols(df: DataFrame) -> DataFrame:
    for col_name in df.columns:
        df = df.withColumnRenamed(col_name, humps.decamelize(col_name.replace("-", "_")))

    return df


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str):
    df.select(col_names).write.insertInto(table_name, overwrite=False)


def etl_steps(env: dict, spark: SparkSession, sc: SparkContext, file_path: str) -> list:

    read_data = read_encrypted_file(env, file_path)
    read_data = restructure_page_data_dict(read_data) if "page_data_" in file_path else read_data

    print(f"Processing dataframe...")
    df = create_json_dataframe(spark, sc, read_data)
    _, table_class = retrieve_table_class(file_path)
    df = explode_df(df, table_class) if table_class.is_explodable else df
    df = explode_breakdowns_df(df) if table_class.has_breakdown else df
    df = rename_df_cols(df)
    df_final, schema_report = reformat_df_data_field_types2(df, table_class)
    print(f"Writing dataframe to {table_class.table_name} table...")
    spark.sql(table_class.create_table())
    table_schema = table_class.get_spark_schema()
    write_files_to_tables(df_final, table_schema.names, table_class.table_name)
    print(f"Done...")

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
    proccessed_files_query = get_proccessed_files_query(file_helper.file_paths)
    if file_helper.file_paths:
        file_paths = remove_processed_files(spark, file_helper.file_paths, proccessed_files_query)

    if not file_helper.file_paths:
        print("Exiting run:\n" + "\n".join(file_helper.get_s3_files_exceptions))
        return spark, [], file_helper.duration_s

    spark.sql(f"create database if not exists {db_name};")

    print(f"{len(file_helper.file_paths)} files to process")

    data_source_n_status = []

    for path in file_helper.file_paths:
        logger_helper = LoggerHelper(source=path, path_n_sizes=file_helper.paths_n_sizes)
        class_name, _ = retrieve_table_class(path, just_class_name=True)
        try:
            schema_report = etl_steps(env, spark, sc, path)
            logger_helper.log_status(schema_report=schema_report)

        except Exception as e:
            msg = f"Error on {class_name} data\n{traceback.format_exc()}"
            logger_helper.log_status(traceback=msg, failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
