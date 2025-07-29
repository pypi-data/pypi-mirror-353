# Databricks notebook source
from typing import Tuple
import os
import traceback
import datetime as dt

from pyspark.sql import SparkSession

from ETL.scripts.meta_ads.df_utils.meta_ads_df_utils import *
from ETL.scripts.meta_ads.df_utils.commons import create_json_files_dataframe, collate_missed_fields, write_df_to_tables
from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/meta_ads_s3_backdate.py"

table_class_campaign = CampaignInsightTable()
table_class_ads = AdsInsightTable()
backdate_start = dt.date(2024, 10, 10).strftime("%Y/%m/%d")
backdate_end = dt.date(2025, 2, 2).strftime("%Y/%m/%d")


def get_source_files(env):
    breadcrumbs = ["landing/meta_ads/insights"]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs, date_range={"start": backdate_start, "end": backdate_end})

    return file_helper


def etl_steps(spark: SparkSession, file_paths: list, overwrite: bool):
    df_meta_ads = create_json_files_dataframe(spark, file_paths)
    response_time_col = ["response_time"] if "response_time" in df_meta_ads.columns else []
    df_campaign = df_meta_ads.selectExpr(["explode_outer(campaign_insights) campaign_insights"] + response_time_col)
    df_ads = df_meta_ads.selectExpr(["explode_outer(ads_insights) ads_insights"] + response_time_col)

    df_campaign = df_campaign.selectExpr(["campaign_insights.*"] + response_time_col).na.drop("all")
    df_ads = df_ads.selectExpr(["ads_insights.*"] + response_time_col).na.drop("all")

    df_campaign, _schema_report_c = reformat_df_data_field_types2(df_campaign, table_class_campaign)
    df_ads, _schema_report_a = reformat_df_data_field_types2(df_ads, table_class_ads)
    schema_reports = [_schema_report_c, _schema_report_a]

    spark.sql(table_class_campaign.create_table())
    spark.sql(table_class_ads.create_table())

    write_df_to_tables(df_campaign, table_class_campaign.table_name, table_class_campaign.get_spark_schema().names, overwrite_mode=overwrite)
    write_df_to_tables(df_ads, table_class_ads.table_name, table_class_ads.get_spark_schema().names, overwrite_mode=overwrite)

    return schema_reports


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="meta_ads_backdate"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    file_helper = get_source_files(env)

    spark.sql(f"create database if not exists {db_name}")
    data_source_n_status = []

    overwrite_mode = False
    batch_number = 1
    batch_increment = 10

    for indx in range(0, len(file_helper.file_paths), batch_increment):
        batch_paths = file_helper.file_paths[indx:indx + batch_increment]
        logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
        try:
            print(f"Batch {batch_number} - Reading meta_ads data files to memory...")
            schema_reports = etl_steps(spark, batch_paths, overwrite_mode)
            end_indx = indx + batch_increment if indx + batch_increment < len(file_helper.file_paths) else len(file_helper.file_paths)
            print(
                f"Wrote {indx}:{end_indx} data range of {len(file_helper.file_paths)} into meta_ads tables with {'overwrite' if overwrite_mode else 'append'} mode\n")

            batch_number += 1
            logger_helper.log_status(schema_report=schema_reports)

        except Exception as e:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)
            print(traceback.format_exc())

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())
