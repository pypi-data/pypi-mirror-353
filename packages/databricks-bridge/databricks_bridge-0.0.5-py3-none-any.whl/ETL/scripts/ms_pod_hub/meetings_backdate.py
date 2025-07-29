# Databricks notebook source
from typing import Tuple
from pyspark.sql import SparkSession
import traceback
import os

from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info
from ETL.scripts.ms_pod_hub.meetings_df_utils import MeetingsTable
from ETL.scripts.ms_pod_hub.df_utils.commons import etl_steps_meetings, split_files_by_date

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/meetings.py"

table_class = MeetingsTable()
min_date = "2023/07/23"
max_date = "2023/10/22"


def get_source_files(env):
    breadcrumbs = ["landing/ms-pod-hub/MeetingEvent"]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs, date_range={"start": min_date, "end": max_date})

    return file_helper


@log_general_info(
    env=locals(),
    etl_data="meetings",
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    data_source_n_status = []
    file_helper = get_source_files(env)
    file_per_date_dict = split_files_by_date(file_helper.file_paths)
    file_dates = list(file_per_date_dict.keys())
    file_dates.sort(reverse=False)  # sort in ascending order
    
    df_schema = table_class.get_spark_schema()
    spark.sql(f"create table {table_class.table_name}_bkp as select * from {table_class.table_name}")

    for file_date in file_dates:
        paths = file_per_date_dict[file_date]
        print(f"processing {len(paths)} files for file_date: {file_date}")

        batch_number = 1
        batch_increment = 1000
        overwrite_mode = False

        for indx in range(0, len(paths), batch_increment):
            batch_paths = paths[indx:indx + batch_increment]
            logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
            print(f"Batch {batch_number} - Reading {table_class.__class__.__name__} data files data to memory...")

            try:
                schema_report = etl_steps_meetings(spark, batch_paths, table_class)
                end_indx = indx + batch_increment if indx + batch_increment < len(paths) else len(paths)
                print(f"Wrote {indx}:{end_indx} data range of {len(paths)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")

                batch_number += 1
                logger_helper.log_status(schema_report=schema_report)
            except Exception:
                logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

            data_source_n_status.append(logger_helper.source_n_status)

    print(f"The backup table still exists in {table_class.table_name}_bkp ")

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
