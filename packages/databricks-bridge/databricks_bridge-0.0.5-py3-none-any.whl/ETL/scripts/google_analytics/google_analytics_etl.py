# Databricks notebook source
from typing import Tuple
import os
import json
import traceback
import datetime as dt

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.dataframe import DataFrame, SparkContext
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

from ETL.scripts.google_analytics.df_utils.google_analytics_df_utils import *
from ETL.commons.google_auth import get_token_path, service_account_auth
from ETL.commons.reformat_data import reformat_df_data_field_types2, rename_df_cols
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/google_analytics_etl.py"
report_date = (dt.date.today() - dt.timedelta(days=1)).strftime("%Y-%m-%d")


def google_analytics_auth():
    key_file_path = get_token_path(ga4=True)
    client = service_account_auth(key_file_path=key_file_path)
    return client


def google_analytics_api_call(client, dimensions: list, metrics: list):
    property_id = "344436016"
    dimensions = [Dimension(name=el) for el in dimensions]
    metrics = [Metric(name=el) for el in metrics]
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=dimensions,
        metrics=metrics,
        date_ranges=[DateRange(start_date=report_date, end_date=report_date)],
    )
    response = client.run_report(request)
    return response


def reformat_response_structure(response):
    response_data = []
    for row in response.rows:
        dimensions_data = {response.dimension_headers[i].name: row.dimension_values[i].value for i in
                           range(len(row.dimension_values))}
        metrics_data = {response.metric_headers[i].name: row.metric_values[i].value for i in
                        range(len(row.metric_values))}
        response_data.append({**dimensions_data, **metrics_data})

    return response_data


def create_json_dataframe(spark: SparkSession, sc: SparkContext, dict_list: list) -> DataFrame:
    # Load data into spark dataframe
    return spark.read.json(sc.parallelize([json.dumps(dict_list)]))


def rename_target_columns(df: DataFrame, table_class):
    for old_col, new_col in table_class.rename_cols.items():
        df = df.withColumnRenamed(old_col, new_col)
    return df


def write_df_to_tables(df: DataFrame, table_name: str, col_names: list, overwrite_mode: bool = False):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite_mode)


def etl_steps(spark: SparkSession, sc: SparkContext, response, table_class):
    response_data = reformat_response_structure(response)
    df = create_json_dataframe(spark, sc, response_data)
    df = rename_target_columns(df, table_class)
    df = rename_df_cols(df)
    df = df.withColumn("report_date", F.lit(report_date))
    df, schema_report = reformat_df_data_field_types2(df, table_class)

    spark.sql(table_class.create_table())
    write_df_to_tables(df, table_class.table_name, table_class.get_spark_schema().names, overwrite_mode=False)


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="google_analytics_api"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    spark.sql(f"create database if not exists {db_name}")
    data_source_n_status = []

    client = google_analytics_auth()

    for key, value in analytics_targets.items():
        logger_helper = LoggerHelper(source=f"google analytics api - {key}")
        table_class = value["table_class"]
        try:
            response = google_analytics_api_call(client, value["dimensions"], value["metrics"])
            etl_steps(spark, sc, response, table_class)
            logger_helper.log_status()
        except Exception as e:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)
    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())

# REF: https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema
# REF: https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart-client-libraries
# REF: https://www.lupagedigital.com/blog/google-analytics-api-python/
