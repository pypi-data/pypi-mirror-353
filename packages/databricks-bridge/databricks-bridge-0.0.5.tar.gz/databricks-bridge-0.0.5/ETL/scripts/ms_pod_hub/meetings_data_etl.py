# Databricks notebook source
from typing import Tuple
from pyspark.sql import SparkSession
import traceback
import os

from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info
from ETL.scripts.ms_pod_hub.meetings_df_utils import MeetingsTable, db_name
from ETL.scripts.ms_pod_hub.df_utils.commons import etl_steps_meetings

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/meetings_data_etl.py"

table_class = MeetingsTable()


def get_source_files(env):
    breadcrumbs = ["landing/ms-pod-hub/MeetingEvent"]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs, date_diff=-1)

    return file_helper


@log_general_info(
    env=locals(),
    etl_data="meetings",
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    file_helper = get_source_files(env)

    if not file_helper.file_paths:
        print("Exiting run:\n" + "\n".join(file_helper.get_s3_files_exceptions))
        logger_helper = LoggerHelper(source="landing/ms-pod-hub/MeetingEvent")
        msg = "No files found in following S3 bucket: landing/ms-pod-hub/MeetingEvent"
        logger_helper.log_status(warn=True, traceback=msg)
        return spark, [logger_helper.source_n_status], file_helper.duration_s

    data_source_n_status = []
    spark.sql(f"create database if not exists {db_name};")
    spark.sql(table_class.create_table())

    batch_number = 1
    batch_increment = 1000
    overwrite_mode = False

    for indx in range(0, len(file_helper.file_paths), batch_increment):
        batch_paths = file_helper.file_paths[indx:indx + batch_increment]
        logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
        print(f"Batch {batch_number} - Reading {table_class.__class__.__name__} data files data to memory...")
        try:
            schema_report = etl_steps_meetings(spark, batch_paths, table_class)
            end_indx = indx + batch_increment if indx + batch_increment < len(file_helper.file_paths) else len(file_helper.file_paths)
            print(f"Wrote {indx}:{end_indx} data range of {len(file_helper.file_paths)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")

            batch_number += 1
            logger_helper.log_status(schema_report=schema_report)
        except Exception as e:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
