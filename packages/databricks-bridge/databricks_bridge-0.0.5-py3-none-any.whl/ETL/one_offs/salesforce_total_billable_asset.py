# Databricks notebook source
from typing import Tuple
import humps
import os
import traceback
from pyspark.sql import SparkSession

from ETL.scripts.ms_salesforce_sync.df_utils.ms_salesforce_sync_df_utils import *
from ETL.scripts.ms_salesforce_sync.df_utils.commons import create_csv_dataframe, reformat_df_data_field_types2
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/salesforce_total_billable_asset.py"
# Instantiate table class
table_class = TotalBillableAssetTable()


def get_source_files():
    return [
        "s3a://ytree-dl-landing-zone/landing/salesforce/backups/Total_Billable_Asset__c.csv"
    ]


def etl_steps(spark: SparkSession, file_path):
    df = spark.read.option("header", True).option("multiline", True).csv(file_path)
    for _col in df.columns:
        df = df.withColumnRenamed(_col, humps.decamelize(_col.replace("__c", "").replace("_", "")))
    # Reformat the df to cast the fields with the expected datatype as stated in the table spark schema
    df, schema_report = reformat_df_data_field_types2(df, table_class)
    # Create table is not exist and insert dataframe into table
    spark.sql(table_class.create_table())
    df.select(table_class.get_spark_schema().names).write.insertInto(table_class.table_name, overwrite=True)

    return schema_report


@log_general_info(
    env=locals(),
    etl_data="salesforce_total_billable_asset",
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    spark.conf.set('spark.sql.caseSensitive', True)
    file_paths = get_source_files()

    print(f"Spark UI Url: {spark_ui_url}")
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        spark.sql(f"use catalog {catalog_name}")
    spark.sql(f"create database if not exists {db_name};")

    print(f"{len(file_paths)} files to process")
    data_source_n_status = []

    for file_path in file_paths:
        logger_helper = LoggerHelper(source=file_path)
        try:
            schema_report = etl_steps(spark, file_path)
            logger_helper.log_status(schema_report=schema_report)

        except Exception:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())
