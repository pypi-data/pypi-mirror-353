# Databricks notebook source
from typing import Tuple

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import arrays_zip, explode
import traceback
import os
import humps
from datetime import datetime

from ETL.scripts.asset.df_utils.morningstar_json_df_utils import *
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper, remove_logged_processed_files, SchemaReport
from ETL.commons.reformat_data import (
    camel_to_snake_case_df, df_targeted_explosion, reformat_df_data_field_types2
)
from ETL.commons.normalize_data import get_nested_df_paths
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/all_morningstar_json.py"
etl_data_name = "asset_morningstar_json"


def get_source_files(env):
    breadcrumbs = [
        "landing/asset/public_listed/morningstar/json/isin/live-price",
        "landing/asset/public_listed/morningstar/json/isin/full-response",
        "landing/asset/public_listed/morningstar/json/msid/full-response",
        "landing/asset/public_listed/morningstar/json/msid/market-price",
        "landing/asset/public_listed/morningstar/json/msid/total-return-index"
    ]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs, date_diff=-1)

    return file_helper


def get_filename_attr(file_path: str) -> str:

    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        file_tag = "_".join(file_path.split("/")[-5].lower().split("-"))
        sort_id = file_path.split("/")[-6]
    else:
        file_tag = "_".join(file_path.split("/")[-2].split("_")[3].lower().split("-"))
        sort_id = file_path.split("/")[-2].split("_")[2]

    class_name = humps.pascalize(file_tag) + f"{sort_id.upper()}Table"

    return class_name


def normalize_nested_df(df: DataFrame, explodables: dict) -> DataFrame:
    nested_children = [col.split(".")[-1] for key, nested_field in explodables.items() for col in nested_field]
    all_paths, expected_query_paths = get_nested_df_paths(df, nested_children)
    select_expression = [f"{path} as {humps.decamelize(path.replace('[0]', '').replace('.', '_')).replace('__', '_')}" for path in expected_query_paths]
    detail_df = df.selectExpr(select_expression)
    arrays_zip_args = ", ".join([f"'{col}'" for col in detail_df.columns if col[-3:] != "_id"])
    final_explosion_select_expression = [f"{'tmp.'+col if col in arrays_zip_args else col+'[0] as '+col}" for col in detail_df.columns]
    normalized_df = detail_df.withColumn("tmp", eval(f"arrays_zip({arrays_zip_args})")).withColumn("tmp", explode("tmp")).selectExpr(final_explosion_select_expression)

    return normalized_df


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


def etl_steps(
        spark: SparkSession, table_class, batch_paths: list, deeply_nested: bool, overwrite_mode: bool
) -> SchemaReport:

    print(f"Writing data into dataframes...")
    start_time = datetime.now()
    df = create_json_dataframe(spark, batch_paths)
    df = camel_to_snake_case_df(df)

    if deeply_nested:
        df = normalize_nested_df(df, table_class.explodables) if df.count() > 0 else df
    else:
        df = df_targeted_explosion(df, table_class.explodables) if df.count() > 0 else df

    df_final, schema_report = reformat_df_data_field_types2(df, table_class)
    spark.sql(table_class.create_table())
    table_schema = table_class.get_spark_schema()
    write_files_to_tables(df_final, table_schema.names, table_class.table_name, overwrite_mode)

    print(f"Done! Duration: {(datetime.now() - start_time).total_seconds()} seconds")

    return schema_report


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str, overwrite_mode: bool):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite_mode)


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
    for db in db_name:
        spark.sql(f"create database if not exists {db};")

    print(f"{len(file_helper.file_paths)} files to process")

    deeply_nested_data_classes = ["MarketPriceMSIDTable", "TotalReturnIndexMSIDTable"]
    data_source_n_status = []
    file_paths_per_data_class = {}
    for path in file_helper.file_paths:
        class_name = get_filename_attr(path)
        if class_name not in file_paths_per_data_class:
            file_paths_per_data_class[class_name] = []

        file_paths_per_data_class[class_name] += [path]

    for class_name, paths in file_paths_per_data_class.items():
        table_class = eval(class_name + "()")
        missed_fields = []
        overwrite_mode = True
        batch_number = 1
        batch_increment = 1000
        deeply_nested = True if class_name in deeply_nested_data_classes else False

        print(f"\nProcessing {len(paths)} files in total for {class_name}...\n")

        for indx in range(0, len(paths), batch_increment):
            batch_paths = paths[indx:indx + batch_increment]
            logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
            try:
                print(f"Batch {batch_number} - Reading {class_name} data files data to memory...")

                schema_report = etl_steps(spark, table_class, batch_paths, deeply_nested, overwrite_mode)

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
