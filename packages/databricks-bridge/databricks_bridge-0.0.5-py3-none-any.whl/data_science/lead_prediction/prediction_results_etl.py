# Databricks notebook source
from typing import Tuple
import os
import traceback
import pandas as pd
import numpy as np
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
import pyspark.sql.functions as f

from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

from data_science.lead_prediction.df_utils.lead_prediction_df_utils import *
from ETL.commons.reformat_data import reformat_df_data_field_types2


set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/prediction_results_etl.py"

table_class = LeadPredictionResultsTable()

today_date = datetime.today().strftime('%B_%m%d%Y')
# Create the file name
file_name = f"{today_date}.csv"
print(file_name)
path="/dbfs/FileStore/Lead_Pred_test"
file_name_with_prefix = "Final_Predicted_dates_" + file_name


def retrieve_source_df() -> pd.DataFrame:
    file_path = f"{path}/{file_name_with_prefix}"
    print(f"\nretrieving file from: {path}/{file_name}\n")
    final_completion_dates_prediction = pd.read_csv(file_path)
    return final_completion_dates_prediction


def select_columns_from_pd_df(final_completion_dates_prediction: pd.DataFrame) -> pd.DataFrame:
    selected_columns = ['id_lead_tbl', 'formatted_est_billable_assets_opp_tbl', 'current_stage_opp_tbl',
                        'predicted_stage', 'predicted_date']
    new_df = final_completion_dates_prediction[selected_columns].copy()

    return new_df


def filter_pd_df(new_df: pd.DataFrame):
    new_df['predicted_date'] = pd.to_datetime(new_df['predicted_date'])

    current_month = datetime.now().month
    next_month = (datetime.now().month % 12) + 1

    filtered_df = new_df[(new_df['predicted_date'].dt.month == current_month) |
                         (new_df['predicted_date'].dt.month == next_month)]
    filtered_df = filtered_df.rename(columns={'current_stage_opp_tbl': 'current_stage'})
    filtered_df['predicted_stage'] = filtered_df['predicted_stage'].replace(8, 'Complete')

    # display(filtered_df)

    return filtered_df


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str, overwrite: bool = False):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite)


def etl_steps(spark: SparkSession):
    final_completion_dates_prediction = retrieve_source_df()
    new_df = select_columns_from_pd_df(final_completion_dates_prediction)
    filtered_df = filter_pd_df(new_df)
    df_spark = spark.createDataFrame(filtered_df)
    df_spark = df_spark.withColumn("insert_timestamp", f.lit(datetime.now()))
    df_spark, schema_report = reformat_df_data_field_types2(df_spark, table_class)
    table_schema = table_class.get_spark_schema()
    write_files_to_tables(df_spark, table_schema.names, table_class.table_name)

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

    data_source_n_status = []

    logger_helper = LoggerHelper(source=f"{path}/{file_name_with_prefix}")
    try:
        schema_report = etl_steps(spark)
        logger_helper.log_status(schema_report=schema_report)

    except Exception as e:
        msg = f"Error running predicting_days_model:\n{traceback.format_exc()}"
        logger_helper.log_status(traceback=msg, failed=True)

    data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())
