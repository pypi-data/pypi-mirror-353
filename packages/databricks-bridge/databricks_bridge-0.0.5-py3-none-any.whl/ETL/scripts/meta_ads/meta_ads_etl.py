# Databricks notebook source
from typing import Tuple
import os
import traceback
import datetime as dt

from pyspark.sql import SparkSession

from ETL.scripts.meta_ads.df_utils.meta_ads_df_utils import *
from ETL.scripts.meta_ads.df_utils.commons import get_api_secrets, get_campaign_and_ad_ids, etl_steps
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/meta_ads_etl.py"

table_class_campaign = CampaignInsightTable()
table_class_ads = AdsInsightTable()
target_date = (dt.date.today() - dt.timedelta(days=1)).strftime("%Y-%m-%d")


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="meta_marketing_api"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    spark.sql(f"create database if not exists {db_name}")
    data_source_n_status = []

    secrets = get_api_secrets(env)
    logger_helper = LoggerHelper(source=f"campaign and ad ids retrieval")
    campaign_ad_ids = []

    try:
        campaign_ad_ids = get_campaign_and_ad_ids(secrets=secrets)
        logger_helper.log_status()
    except Exception as e:
        logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

    data_source_n_status.append(logger_helper.source_n_status)

    overwrite = False
    for campaign in campaign_ad_ids:
        logger_helper = LoggerHelper(source=f"campaign_id: {campaign['campaign_id']}, ad_ids: {campaign['ad_ids']}")
        print(f"\nProcessing for campaign_id: {campaign['campaign_id']}")
        try:
            schema_reports = etl_steps(spark, sc, secrets, campaign, target_date, overwrite)
            logger_helper.log_status(schema_report=schema_reports)
            overwrite = False
        except Exception as e:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    print("\n")
    spark.sql(table_class_campaign.create_actions_view())
    spark.sql(table_class_ads.create_actions_view())

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())

# REF: https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights#fields
