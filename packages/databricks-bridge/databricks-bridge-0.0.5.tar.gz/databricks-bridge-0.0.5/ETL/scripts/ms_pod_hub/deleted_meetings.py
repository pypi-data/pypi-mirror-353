# Databricks notebook source
from typing import Tuple
import traceback
import os

from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException

from ETL.scripts.ms_pod_hub.df_utils.commons import create_json_dataframe, remove_any_rows_existing_in_hive_table
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info
from ETL.scripts.ms_pod_hub.meetings_df_utils import MeetingsTable

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/deleted_meetings.py"


def get_source_files(env):
    breadcrumbs = ["landing/ms-pod-hub/MeetingDeletedEvent"]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs, date_diff=-1)

    return file_helper


@log_general_info(
    env=locals(),
    etl_data="deleted_meetings",
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    data_source_n_status = []
    file_helper = get_source_files(env)
    
    # Instantiating the table
    table_class = MeetingsTable()

    batch_number = 1
    batch_increment = 1000
    overwrite_mode = False

    for indx in range(0, len(file_helper.file_paths), batch_increment):
        batch_paths = file_helper.file_paths[indx:indx + batch_increment]
        logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
        try:
            df = create_json_dataframe(spark, batch_paths)
            remove_any_rows_existing_in_hive_table(spark, df, table_class.table_name)
            logger_helper.log_status()

        except AnalysisException as e:
            # Handle schema-related errors
            logger_helper.log_status(warn=True, traceback=str(e))

        except Exception as e:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
