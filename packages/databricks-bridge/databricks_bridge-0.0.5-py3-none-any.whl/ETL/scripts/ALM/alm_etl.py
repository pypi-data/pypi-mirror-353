# Databricks notebook source
from typing import Tuple
import os
import traceback
import humps

from pyspark.sql import SparkSession
from ETL.scripts.ALM.df_utils.alm_df_utils import *
from ETL.scripts.ALM.df_utils.common_fcns import updated_etl_steps, remove_processed_files, partition_files

from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info


set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/alm_etl.py"


def get_source_files(env):
    breadcrumbs = [
        "landing/alm/ALM_EVENTS/ALM_OUT_DATA_UPDATED",
        "landing/alm/MS_ALM_EVENT_TOPIC/EDUCATIONAL_EXPENSE_UPDATED",
        "landing/alm/MS_ALM_EVENT_TOPIC/ELDERLY_CARE_EXPENSE_UPDATED",
        "landing/alm/MS_ALM_EVENT_TOPIC/GENERAL_EXPENSE_UPDATED",
        "landing/alm/MS_ALM_EVENT_TOPIC/HOUSE_EXPENSE_UPDATED",
        "landing/alm/MS_ALM_EVENT_TOPIC/INCOME_UPDATED",
        "landing/alm/MS_ALM_EVENT_TOPIC/GROSS_INCOME_UPDATED",
        "landing/alm/MS_ALM_EVENT_TOPIC/SAVINGS_UPDATED",
        "landing/alm/MS_ALM_EVENT_TOPIC/SETTINGS_UPDATED",
    ]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs, date_diff=-1)

    return file_helper


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")
    file_helper = get_source_files(env)
    if file_helper.file_paths:
        file_helper.file_paths = remove_processed_files(spark, file_helper.file_paths, etl_data_name)
    print(f"{len(file_helper.file_paths)} files to process")

    if not file_helper.file_paths:
        print("Exiting run:\n" + "\n".join(file_helper.get_s3_files_exceptions))
        return spark, [], file_helper.duration_s

    partitioned_file_paths = partition_files(file_helper.file_paths)

    spark.sql(f"create database if not exists {db_name};")

    data_source_n_status = []

    for event_topic, v in partitioned_file_paths.items():
        for event_type, file_paths in v.items():
            event_suffix = event_type.lower().split("_")[-1]
            class_name = humps.pascalize(event_type.lower().replace(event_suffix, "table"))
            print(class_name)
            table_class = eval(f"{class_name}('{event_suffix}')")

            batch_number = 1
            batch_increment = 1000
            overwrite_mode = False

            for indx in range(0, len(file_paths), batch_increment):
                batch_paths = file_paths[indx:indx + batch_increment]
                logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
                try:
                    print(f"Batch {batch_number} - Reading {class_name} data files data to memory...")
                    schema_report = updated_etl_steps(spark, batch_paths, table_class)
                    end_indx = indx + batch_increment if indx + batch_increment < len(file_paths) else len(file_paths)
                    print(
                        f"Wrote {indx}:{end_indx} data range of {len(file_paths)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")

                    batch_number += 1
                    logger_helper.log_status(schema_report=schema_report)

                except Exception as e:
                    logger_helper.log_status(traceback=traceback.format_exc(), failed=True)
                    print(traceback.format_exc())

                data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
