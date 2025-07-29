# Databricks notebook source
from typing import Tuple
import os
import json
import traceback

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame, SparkContext

from google.ads.googleads.client import GoogleAdsClient

from ETL.scripts.google_ads.df_utils.google_ads_df_utils import *
from ETL.commons.unittest_utils import create_tempfile_from_string_data
from ETL.commons.google_auth import get_token_path, get_gcloud_api_creds, auth, read_json_file
from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/google_ads_etl.py"

table_class = AdsMetricsTable()

SCOPES = [
    "https://www.googleapis.com/auth/adwords",
    "https://www.googleapis.com/auth/cloud-platform"
]
developer_token = ""
customer_id = ""


def update_client_creds():
    token_dict = read_json_file(get_token_path(gads=True))
    credentials = {
        "developer_token": developer_token,
        "refresh_token": token_dict["refresh_token"],
        "client_id": token_dict["client_id"],
        "client_secret": token_dict["client_secret"],
        "use_proto_plus": True
    }
    return credentials


def google_ads_auth(env: dict):
    token_path = get_token_path(gads=True)
    creds_dict = get_gcloud_api_creds(env)
    creds_file_dir = create_tempfile_from_string_data(json.dumps(creds_dict).encode())
    creds = auth(creds_file_dir, scopes=SCOPES, token_path=token_path)
    token_dict = read_json_file(token_path)
    client_creds = update_client_creds()
    client = GoogleAdsClient.load_from_dict(client_creds)

    return client


def create_json_dataframe(spark: SparkSession, sc: SparkContext, dict_list: list) -> DataFrame:
    # Load data into spark dataframe
    return spark.read.json(sc.parallelize([json.dumps(dict_list)]))


def write_df_to_tables(df: DataFrame, table_name: str, col_names: list, overwrite_mode: bool = False):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite_mode)


def execute_google_ads_query(service, query: str):
    return service.search_stream(customer_id=customer_id, query=query)


def build_results_dict_list(stream, field_alias: dict):
    _dict_list = []
    for batch in stream:
        for row in batch.results:
            result_dict = {}
            for field, alias in field_alias.items():
                result_dict[alias] = eval(f"row.{field}")
            _dict_list.append(result_dict)

    return _dict_list


def etl_steps(spark: SparkSession, sc: SparkContext, service):
    # breakpoint
    # campaign_query = """SELECT campaign.id, campaign.name FROM campaign ORDER BY campaign.id"""
    # stream = ga_service.search_stream(customer_id='5108523815', query=campaign_query)
    #
    # campaign_dict_list = []
    # for batch in stream:
    #     for row in batch.results:
    #         campaign_dict_list.append({"campaign_id": row.campaign.id, "campaign_name": row.campaign.name})

    stream = execute_google_ads_query(service, get_ads_metrics_query())
    ads_dict_list = build_results_dict_list(stream, get_ads_metric_fields())

    df = create_json_dataframe(spark, sc, ads_dict_list)
    df, schema_report = reformat_df_data_field_types2(df, table_class)

    spark.sql(table_class.create_table())
    write_df_to_tables(df, table_class.table_name, table_class.get_spark_schema().names, overwrite_mode=False)


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="google_marketing_api"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    spark.sql(f"create database if not exists {db_name}")
    data_source_n_status = []

    client = google_ads_auth(env)
    ga_service = client.get_service("GoogleAdsService")

    logger_helper = LoggerHelper(source="google ads api")
    try:
        etl_steps(spark, sc, ga_service)
        logger_helper.log_status()
    except Exception as e:
        logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

    data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())

# REF: https://developers.google.com/google-ads/api/samples/get-campaigns
# REF: https://developers.google.com/google-ads/api/fields/v17/metrics
