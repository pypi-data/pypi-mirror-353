import functools
import os
from datetime import datetime, date

from ETL.logging.df_utils.logging_df_utils import *
from ETL.logging.df_utils.commons import (
    extract_etl_files, insert_log_into_logging_table, show_fail_and_warning_logs, get_past_runs_files_count,
    trigger_files_discrepancy_alert
)

is_databricks = os.environ.get('ISDATABRICKS', 'local') == "TRUE"
catalog_name = "hive_metastore"


def log_general_info(env, etl_data: str, script_path: str, data_sources_type: str):
    start_time = datetime.now()

    def decorator_log_general_info(func):
        @functools.wraps(func)  # preserves decorated function identity
        def wrapper_log_general_info(*args, **kwargs):
            spark, data_source_n_status, get_data_sources_duration_s = func(*args, **kwargs)  # run_etl
            # Calculate execution duration
            end_time = datetime.now()
            datetime_diff = end_time - start_time
            duration_s = datetime_diff.total_seconds()
            # Collect logging table data
            logging_data = {"etl_data": etl_data, "date_executed": date.today(), "start_time": start_time,
                            "end_time": end_time, "total_duration_secs": duration_s, "script_path": script_path,
                            "get_data_sources_duration_secs": get_data_sources_duration_s,
                            "data_source_n_status": data_source_n_status, "data_source_type": data_sources_type}

            if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
                spark.sql(f"use catalog {catalog_name};")
            etl_files = extract_etl_files(data_source_n_status) if data_sources_type == "datalake" else []
            df_file_cnt = get_past_runs_files_count(spark, etl_data) if etl_files and is_databricks else None
            df_log = insert_log_into_logging_table(env, spark, GeneralInfoTable(), logging_data)
            show_fail_and_warning_logs(env, spark, df_log)  # show log table
            if is_databricks:
                trigger_files_discrepancy_alert(env, spark, etl_files, df_file_cnt) if etl_files else None

        return wrapper_log_general_info
    return decorator_log_general_info
