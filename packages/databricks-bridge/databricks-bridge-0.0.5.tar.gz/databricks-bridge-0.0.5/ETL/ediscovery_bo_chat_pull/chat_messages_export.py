# Databricks notebook source
from typing import Tuple
import os
import traceback
import humps

from pyspark.sql import SparkSession, functions as f

from ETL.ediscovery_bo_chat_pull.df_utils.chat_messages_export_df_utils import *
from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info


set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/chat_messages_export.py"
parent_path = "dbfs:/FileStore/etl_files/ediscovery_bo_chat_pull_export"
table_class = ChatDecryptedTable()


def etl_steps(spark: SparkSession):
    df = spark.read.option("inferSchema", "true").option("header", True).option("multiline", True).csv(parent_path)
    df = df.withColumn("file_path", f.input_file_name())
    df = df.withColumn("export_date", f.split(f.col("file_path"), '/').getItem(4))\
        .withColumn("export_date", f.split(f.col("export_date"), '%').getItem(0))
    df = df.withColumn("client_id", f.split(f.col("file_path"), '/').getItem(4))\
        .withColumn("client_id", f.split(f.col("client_id"), 'Profile%20').getItem(1))\
        .withColumn("client_id", f.regexp_replace(f.col("client_id"), '.csv', ''))
    df = df.withColumn("from_to_date", f.split(f.col("file_path"), '\(').getItem(1))\
        .withColumn("from_to_date", f.split(f.col("from_to_date"), '\)').getItem(0))\
        .withColumn("from_date", f.split(f.col("from_to_date"), '_').getItem(0))\
        .withColumn("to_date", f.split(f.col("from_to_date"), '_').getItem(1))

    df = df.drop(*["file_path", "from_to_date"])
    for _col in df.columns:
        df = df.withColumnRenamed(_col, humps.decamelize(_col.replace(" ", "_")).replace("__", "_"))

    df, schema_report = reformat_df_data_field_types2(df, table_class)

    df.select(table_class.get_spark_schema().names).write.insertInto(table_class.table_name, overwrite=True)
    return schema_report


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="lakehouse"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    spark.sql(f"create database if not exists {db_name};")
    spark.sql(table_class.create_table())

    logger_helper = LoggerHelper(source=parent_path)
    try:
        schema_report = etl_steps(spark)
        logger_helper.log_status(schema_report=schema_report)
    except Exception as e:
        logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

    return spark, [logger_helper.source_n_status], 0.0


if __name__ == "__main__":
    run_etl(locals())
