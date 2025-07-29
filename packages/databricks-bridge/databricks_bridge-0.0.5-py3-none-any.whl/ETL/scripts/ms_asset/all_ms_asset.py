# Databricks notebook source
from datetime import datetime
from typing import Tuple
from pyspark.sql.dataframe import DataFrame
from pyspark.sql import SparkSession, functions as F
import json
import traceback
import os

from ETL.scripts.ms_asset.df_utils.ms_asset_df_utils import *
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info
from ETL.commons.normalize_data import unnest_array_struct_df
from ETL.commons.reformat_data import add_file_arrival_date_df, reformat_df_data_field_types2, rename_df_cols

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/all_ms_asset.py"


def get_source_files(env):
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs="landing/asset/ms_asset")
    return file_helper


# extract currency_code and conversion_rate from collection_currency_exposure
def extract_collection_data(spark: SparkSession, df: DataFrame, file_tag: str) -> DataFrame:
    if file_tag == "collection_currency_exposure":
        # currency_codes = df.select("collection.*").columns
        collection_json = df.select("isin", "collection").toJSON().collect()
        collection_dict_list = [json.loads(item) for item in collection_json]
        for i in range(len(collection_dict_list)):
            collection_dict_list[i]["collection"] = [{"currency_code": key, "conversion_rate": val} for key, val in
                                                     collection_dict_list[i]["collection"].items()]

        collection_df = spark.read.json(spark.sparkContext.parallelize(collection_dict_list))
        collection_df = collection_df\
            .withColumnRenamed("collection", "new_collection")\
            .withColumnRenamed("isin", "new_isin")
        df = df.join(collection_df, df.isin == collection_df.new_isin, "left")
        df = df.drop("collection").drop("new_isin")
        df = df.withColumnRenamed("new_collection", "collection")
    return df


def get_filename_attr(file_path: str) -> Tuple[str, str, str]:
    file_prefix = file_path.split("/")[-1].split("|")[-1].split("_")[0].lower()
    file_tag = "_".join(file_path.split("/")[-1].split("|")[-1].split("_")[2:]).replace(".json", "").lower()
    file_tag = "asset" if file_tag == "" else file_tag
    class_name = "".join([tag.capitalize() for tag in file_tag.split("_")]) + "Table"

    return file_prefix, file_tag, class_name


def create_json_dataframe(spark: SparkSession, paths: list) -> DataFrame:
    # Load read data from json files into spark dataframe
    try:
        # for json files with all \n and \r characters replaced with " "
        df = spark.read.options(mode="FAILFAST").json(paths)
    except Exception as e:
        print(f"malformed records found (i.e _corrupt_records columns):\n{str(e)[:400]}")
        # for json files with all \n and \r characters retained
        df = spark.read.json(paths, multiLine=True)
    return df


def add_file_path(df: DataFrame):
    return df.withColumn("file_path", F.input_file_name())


def explode_struct_columns(df: DataFrame, explodables: list, unappendable_prefixes: list):
    status = [row["status"] for row in df.select("status").distinct().collect()][0]
    df = df.drop("rowInfo") if "rowInfo" in df.columns else df
    df = df.drop("status") if "status" in df.columns else df
    for explode_col in explodables:
        if explode_col in df.columns:
            child_cols = [f"{explode_col}.{el} as {explode_col}_{el}" for el in df.select(f"{explode_col}.*").columns]
            df = df.selectExpr(["*"]+child_cols)
            df = df.drop(explode_col)
            if explode_col in unappendable_prefixes:
                for _col in df.columns:
                    if _col[:len(f"{explode_col}_")] == f"{explode_col}_":
                        df = df.withColumnRenamed(_col, _col[len(f"{explode_col}_"):])
    return df, status


def unnest_df(df: DataFrame, explodables: dict):
    df = unnest_array_struct_df(df, explodables, unappendable_parent_keys)
    return df


def decapitalize_columns(df: DataFrame, expected_columns: list):
    for _col in df.columns:
        if _col.lower() in expected_columns:
            df = df.withColumnRenamed(_col, _col.lower())
    return df


def etl_steps(spark: SparkSession, table_class, batch_paths: list, overwrite_mode: bool) -> list:

    file_prefix, file_tag, class_name = get_filename_attr(batch_paths[0])
    print(f"Writing data into dataframes...")
    start_time = datetime.now()
    df = create_json_dataframe(spark, batch_paths)
    df = add_file_path(df)
    df = add_file_arrival_date_df(df, "file_path")
    df, status = explode_struct_columns(df, ["source"], unappendable_parent_keys)
    df = extract_collection_data(spark, df, file_tag)
    df = unnest_df(df, table_class.explodables)
    df = decapitalize_columns(df, table_class.get_spark_schema().names)
    df = rename_df_cols(df)
    df, schema_report = reformat_df_data_field_types2(df, table_class)
    spark.sql(table_class.create_table())
    write_files_to_tables(df, table_class.get_spark_schema().names, table_class.table_name, overwrite_mode)

    return schema_report


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str, overwrite_mode: bool):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite_mode)


@log_general_info(
    env=locals(),
    etl_data="ms_asset",
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
    file_paths_per_data_class = {}
    for path in file_helper.file_paths:
        file_prefix, file_tag, class_name = get_filename_attr(path)
        data_status = path.split("/")[-1].split("|")[-1].split("_")[0].lower()
        table_class = eval(class_name + f"('{data_status}')")
        if table_class.table_name not in file_paths_per_data_class:
            file_paths_per_data_class[table_class.table_name] = []

        file_paths_per_data_class[table_class.table_name] += [path]

    for table_name, paths in file_paths_per_data_class.items():
        file_prefix, file_tag, class_name = get_filename_attr(paths[0])
        data_status = paths[0].split("/")[-1].split("|")[-1].split("_")[0].lower()
        table_class = eval(class_name + f"('{data_status}')")
        overwrite_mode = True
        batch_number = 1
        batch_increment = 100

        print(f"\nProcessing {len(paths)} files in total for {class_name}...\n")

        for indx in range(0, len(paths), batch_increment):
            batch_paths = paths[indx:indx + batch_increment]
            logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
            try:
                print(f"Batch {batch_number} - Reading {class_name} data files data to memory...")

                schema_report = etl_steps(spark, table_class, batch_paths, overwrite_mode)

                end_indx = indx + batch_increment if indx + batch_increment < len(paths) else len(paths)
                print(f"Wrote {indx}:{end_indx} data range of {len(paths)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")
                overwrite_mode = False
                batch_number += 1
                logger_helper.log_status(schema_report=schema_report)

            except Exception as e:
                msg = f"Error on {class_name} data\n{traceback.format_exc()}"
                logger_helper.log_status(traceback=msg, failed=True)

            data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
