# Databricks notebook source
from typing import Tuple
import os
import traceback

from pyspark.sql import SparkSession

from ETL.scripts.FPS.df_utils.fps_df_utils import *
from ETL.scripts.FPS.df_utils.common_fcns import etl_steps

from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/fps_initial_snapshot.py"


def get_source_files(env):
    breadcrumbs = [
        "landing/fps/FPS_SNAPSHOTTED",
        "landing/fps/FPS_V2_SNAPSHOTTED"
    ]
    for i in range(10):
        file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs=breadcrumbs, date_diff=-i)
        if isinstance(file_helper.paths, list) and len(file_helper.paths) > 0:
            # found_snapshot_files = True
            break
    if isinstance(file_helper.paths, str):
        print(f"No snapshot files found for the past 10 days...")
    else:
        print(f"{len(file_helper.paths)} files retrieved.")

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

    if not file_helper.file_paths:
        print("Exiting run:\n" + "\n".join(file_helper.get_s3_files_exceptions))
        return spark, [], file_helper.duration_s

    spark.sql(f"create database if not exists {db_name};")

    print(f"{len(file_helper.file_paths)} files to process")

    data_source_n_status = []
    event_partition = {}
    for path in file_helper.file_paths:
        event = path.split("/")[-5].lower().replace("snapshotted", "saved")
        if event not in event_partition.keys():
            event_partition[event] = [path]
        else:
            event_partition[event].append(path)

    for event, event_files in event_partition.items():
        class_name = "FPSSavedTable" if event == "fps_saved" else "FPSV2SavedTable"
        table_class = eval(f"{class_name}()")
        spark.sql(table_class.delete_table())

        batch_number = 1
        batch_increment = 1000
        overwrite_mode = False

        for indx in range(0, len(event_files), batch_increment):
            batch_paths = event_files[indx:indx + batch_increment]
            logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
            try:
                print(f"Batch {batch_number} - Reading {class_name} data files data to memory...")
                schema_report = etl_steps(spark, batch_paths, table_class)
                end_indx = indx + batch_increment if indx + batch_increment < len(event_files) else len(event_files)
                print(
                    f"Wrote {indx}:{end_indx} data range of {len(event_files)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")

                batch_number += 1

                logger_helper.log_status(schema_report=schema_report)

            except Exception as e:
                msg = f"Error on {class_name} data\n{traceback.format_exc()}"
                logger_helper.log_status(traceback=msg, failed=True)

            data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())

'''
triggering the snapshot post request in springboot admin

Click the 'Run' button on the row with 'Name' column value as 'Take snapshots for all FPSes.'

staging url: https://ms-spring-boot-admin-jx-staging.jx3.y-tree.uk/scheduled
uat url: https://ms-spring-boot-admin-jx-uat.jx3.y-tree.uk/scheduled
live url: https://ms-spring-boot-admin.y-tree.com/scheduled
'''
