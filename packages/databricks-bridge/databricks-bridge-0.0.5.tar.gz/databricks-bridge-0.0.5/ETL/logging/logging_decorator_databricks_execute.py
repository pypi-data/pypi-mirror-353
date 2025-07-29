import os
import functools
from datetime import datetime, date

from ETL.logging.df_utils.logging_df_utils import *
from ETL.logging.df_utils.commons import insert_log_into_logging_table, show_fail_and_warning_logs

catalog_name = "hive_metastore"


def log_databricks_execute(env):
    start_time = datetime.now()

    def decorator_log_databricks_execute(func):
        @functools.wraps(func)  # preserves decorated function identity
        def wrapper_log_databricks_execute(*args, **kwargs):
            spark, data_source_n_status = func(*args, **kwargs)  # run_etl
            # Calculate execution duration
            end_time = datetime.now()
            datetime_diff = end_time - start_time
            duration_s = datetime_diff.total_seconds()
            # Collect logging table data
            logging_data = {"date_executed": date.today(), "start_time": start_time,
                            "end_time": end_time, "total_duration_secs": duration_s,
                            "data_source_n_status": data_source_n_status}

            if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
                spark.sql(f"use catalog {catalog_name};")

            if data_source_n_status:
                df_log = insert_log_into_logging_table(env, spark, DatabricksExecuteTable(), logging_data)
                show_fail_and_warning_logs(env, spark, df_log, hard_stop=True)  # show log table
            else:
                print("Nothing to log...")

        return wrapper_log_databricks_execute
    return decorator_log_databricks_execute
