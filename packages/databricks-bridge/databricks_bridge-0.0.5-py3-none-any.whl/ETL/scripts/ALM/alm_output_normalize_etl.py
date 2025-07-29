# Databricks notebook source
from typing import Tuple
import os
import traceback

from pyspark.sql import SparkSession
from ETL.scripts.ALM.df_utils.alm_df_utils import *
from ETL.scripts.ALM.df_utils.common_fcns import output_normalize_etl_steps
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info


set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/alm_output_normalize_etl.py"


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

    data_source_n_status = []
    table_class_src = AlmOutDataTable("updated")
    raw_alm_outdata_df = spark.sql(f"select * from {table_class_src.table_name}")
    table_classes = [OutputExpenseTable(), OutputIncomeTable(), OutputWealthTable(), OutputWealthByWrapperTable()]

    for table_class in table_classes:
        logger_helper = LoggerHelper(source=table_class_src.table_name)
        try:
            print(f"Processing {table_class.source_column} column in {table_class_src.table_name}...")
            schema_report = output_normalize_etl_steps(spark, raw_alm_outdata_df, table_class)
            print(f"Wrote normalized data into {table_class.table_name} with overwrite mode\n")

            logger_helper.log_status(schema_report=schema_report)

        except Exception as e:
            msg = f"Error while processing {table_class.source_column} column in {table_class_src.table_name} data"
            logger_helper.log_status(traceback=f"{msg}\n{traceback.format_exc()}", failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())
