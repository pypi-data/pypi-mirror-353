# Databricks notebook source
from typing import Tuple

import os
import traceback
from pyspark.sql import SparkSession

from ETL.scripts.ms_salesforce_sync.df_utils.ms_salesforce_sync_df_utils import *
from ETL.scripts.ms_salesforce_sync.df_utils.commons import get_filename_attr, etl_steps
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info
from ETL.logging.df_utils.commons import send_table_clients_alert

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/all_ms_salesforce_sync.py"


def get_source_files(env):
    breadcrumbs = ["landing/salesforce/ms-salesforce-sync"]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs)
    if file_helper.file_paths:
        file_helper.file_paths = [path for path in file_helper.file_paths if "_all.parquet" in path]

    return file_helper


@log_general_info(
    env=locals(),
    etl_data="ms_salesforce_sync",
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    spark.conf.set('spark.sql.caseSensitive', True)
    file_helper = get_source_files(env)

    if not file_helper.file_paths:
        print(f"Exiting run:\n{file_helper.paths}")
        return spark, [], file_helper.duration_s

    print(f"Spark UI Url: {spark_ui_url}")
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        spark.sql(f"use catalog {catalog_name}")
    spark.sql(f"create database if not exists {db_name};")
    if catalog_name != "hive_metastore":
        spark.sql(mask_fcn_sql)

    print(f"{len(file_helper.file_paths)} files to process")
    data_source_n_status = []

    for file_path in file_helper.file_paths:
        logger_helper = LoggerHelper(source=file_path, path_n_sizes=file_helper.paths_n_sizes)
        # Get file identifiers from filename
        class_name = get_filename_attr(file_path)
        # Instantiate table class
        table_class = eval(f"{class_name}()")
        try:
            schema_report = etl_steps(spark, table_class, file_path, catalog_name=catalog_name)
            logger_helper.log_status(schema_report=schema_report)

        except Exception:
            table_name = table_class.hive_table_name if catalog_name == "hive_metastore" else table_class.table_name
            send_table_clients_alert(env=env, spark=spark, table_name=table_name, catalog=catalog_name)
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    catalog = ""
    env = locals()
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        catalog = env["getArgument"]("catalog")

    catalog_name = catalog if catalog else catalog_name
    run_etl(locals())
