# Databricks notebook source
from typing import Tuple
import os
import traceback

from pyspark.sql import SparkSession, functions as f
from pyspark.sql.dataframe import DataFrame
import ETL.scripts.ms_billing.df_utils.ms_billing_df_utils as df_utils
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

db_prefix = "data_science"
df_utils.db_name = f"{db_prefix}_{df_utils.db_name}" if df_utils.db_name[:12] != db_prefix else df_utils.db_name
db_name = df_utils.db_name
set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/ms_billing_etl.py"
table_class = df_utils.GeneratedMonthlyAccruedRevenueTable()
etl_data_name = df_utils.etl_data_name


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str, overwrite: bool = False):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite)


def etl_steps(df_final: DataFrame, overwrite: bool) -> list:
    table_schema = table_class.get_spark_schema()
    write_files_to_tables(df_final, table_schema.names, table_class.table_name, overwrite=overwrite)
    return []


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
    df_src = spark.sql(f"select * from {table_class.table_name.replace(db_prefix+'_', '')}")
    period_to_unq_list = [row.period_to for row in df_src.select("period_to").distinct().collect()]

    data_source_n_status = []

    batch_number = 1
    overwrite_mode = True

    for period_to in period_to_unq_list:
        source_n_status = {"data_source": f"period_to = {period_to}"}
        try:
            batch_df = df_src.filter(f.expr(f"period_to = '{period_to}'"))
            print(f"Batch {batch_number} - Reading src table where period_to == {period_to}...")
            missed_fields = etl_steps(batch_df, overwrite_mode)
            print(f"Wrote src df where period_to == {period_to} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")
            overwrite_mode = False
            batch_number += 1

            source_n_status["status"] = "success"
            source_n_status["traceback"] = None

        except Exception as e:
            source_n_status["status"] = "fail"
            source_n_status["traceback"] = f"Error where period_to = {period_to}\n{traceback.format_exc()}"

        data_source_n_status.append(source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())
