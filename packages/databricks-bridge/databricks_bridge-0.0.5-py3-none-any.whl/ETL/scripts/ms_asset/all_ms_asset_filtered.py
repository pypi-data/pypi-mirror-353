# Databricks notebook source
from typing import Tuple, List, Any

from pyspark.sql import SparkSession
import humps
import os
import shutil
from datetime import datetime
import traceback
import time

from ETL.scripts.ms_asset.df_utils.ms_asset_df_utils import *
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.commons.ease_of_use_fcns import delete_checkpoint_dir
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/all_ms_asset_filtered.py"


def get_filterable_table_names(file_tags: list) -> list:
    return [eval(humps.pascalize(file_tag)+"Table('').table_name") for file_tag in file_tags]


def get_updated_by_filters(filt_list: list) -> str:
    return "("+", ".join([f"'{el}'" for el in filt_list])+")"


def get_table_file_prefix(table_name: str) -> str:
    return table_name.split('_asset_')[1]


def get_table_file_tag(table_name: str) -> str:
    return table_name.split('_asset_')[-1]


def get_table_names_to_be_filtered(spark: SparkSession, filterable_tables: list) -> Tuple[List[Any], float]:
    start_time = datetime.now()
    all_table_names_rows = spark.sql(f"show tables from {db_name} like 'ms_asset_*'").collect()
    all_table_names = [table_name.tableName for table_name in all_table_names_rows]
    tables_to_filt = [
        table_name for table_name in all_table_names
        if f"{db_name}.{table_name.replace(get_table_file_prefix(table_name),'')}" in filterable_tables and
           "ms_asset_filt_" not in table_name
    ]
    duration_s = (datetime.now() - start_time).total_seconds()
    return tables_to_filt, duration_s


def etl_steps(spark: SparkSession, table_to_filt: str):
    # get table prefix
    table_prefix = get_table_file_prefix(table_to_filt)
    # get table class str
    table_class_str = humps.pascalize(get_table_file_tag(table_to_filt)) + "Table"
    # Instantiate table class
    table_class = eval(table_class_str + f"('filt_{table_prefix}')")
    print(f"\nFilter output Table: {table_class.table_name}\n")
    print(f"data source: {db_name}.{table_to_filt}\n")
    # Create except sql statement
    view_query = f"""
    create or replace view {table_class.table_name} as
    select * from {db_name}.{table_to_filt} where lower(updated_by) not in {updated_by_filters}
    """
    spark.sql(view_query)


filterable_file_tags = ["public", "private", "private_equity", "private_equity_projected_capital_calls"]
filterable_table_names = get_filterable_table_names(filterable_file_tags)
updated_by_to_filt = ["morningstar", "preqin", "cbonds"]
updated_by_filters = get_updated_by_filters(updated_by_to_filt)


@log_general_info(
    env=locals(),
    etl_data="ms_asset_filtered",
    script_path=script_path,
    data_sources_type="lakehouse"
)
def run_etl(env):
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    spark.sparkContext.setCheckpointDir(checkpoint_dir)
    tables_to_be_filtered, get_data_sources_duration_s = get_table_names_to_be_filtered(spark, filterable_table_names)

    print(f"Spark UI Url: {spark_ui_url}")
    spark.sql(f"create database if not exists {db_name};")
    data_source_n_status = []

    for table_to_filt in tables_to_be_filtered:
        logger_helper = LoggerHelper(source=f"{db_name}.{table_to_filt}")
        try:
            etl_steps(spark, table_to_filt)
            logger_helper.log_status()

        except Exception:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    delete_checkpoint_dir(env, checkpoint_dir)

    return spark, data_source_n_status, get_data_sources_duration_s


if __name__ == "__main__":
    run_etl(locals())

# spark.sql("show tables from cleansed like 'ms_asset_filt_*'").show(truncate=False)
# tbl_rows = spark.sql("show tables from cleansed like 'ms_asset_filt_*'").collect()
# table_names_to_del = [tbl_name.tableName for tbl_name in tbl_rows]
# for tbl_name in table_names_to_del: spark.sql(f"drop table if exists cleansed.{tbl_name}")
