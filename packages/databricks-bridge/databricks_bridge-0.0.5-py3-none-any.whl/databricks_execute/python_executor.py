# Databricks notebook source
import subprocess
import traceback
import os
from typing import Tuple

from pyspark.sql import SparkSession

from ETL.logging.logging_decorator_databricks_execute import log_databricks_execute
from ETL.logging.df_utils.logging_df_utils import db_name, DatabricksExecuteTable
from ETL.commons.start_spark_session import get_or_create_spark_session

log_table_class = DatabricksExecuteTable()


def retrieve_all_files():
    pwd = subprocess.check_output(["pwd"]).decode().strip()
    try:
        all_sql_files = [
            f"{pwd}/one_offs_python/{file}"
            for file in subprocess.check_output(["ls", "one_offs_python"]).decode().strip().split("\n")
            if file[-1] != "/"
        ]
    except Exception as e:
        print(e)
        all_sql_files = []

    return all_sql_files


def get_files_to_execute(spark: SparkSession, log_table_name, all_sql_files):
    executed_files = [row.script_path for row in spark.sql(f"select script_path from {log_table_name} where status = 'success';").collect()]
    files_to_execute = [path for path in all_sql_files if f"lakehouse/{path.split('/lakehouse/')[-1]}" not in executed_files]
    files_to_execute.sort()

    return files_to_execute


@log_databricks_execute(
    env=locals()
)
def run_etl(env: dict) -> Tuple[SparkSession, list]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")
    spark.sql(f"create database if not exists {db_name};")
    spark.sql(log_table_class.create_table())

    file_paths = get_files_to_execute(spark, log_table_class.table_name, retrieve_all_files())

    if not file_paths:
        print(f"Exiting run: No one_offs_python scripts to execute...")
        return spark, []

    print(f"{len(file_paths)} files to process")
    data_source_n_status = []

    for file_path in file_paths:
        script_path = f"lakehouse/{file_path.split('/lakehouse/')[-1]}"
        source_n_status = {"script_path": script_path}
        print(f"Executing {script_path} ...")
        try:
            if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
                notebook_path = file_path.split("databricks_execute/")[-1].replace(".py", "")
                env["dbutils"].notebook.run(path=notebook_path, timeout_seconds=18000, arguments={})  # 5hrs timeout
            else:
                subprocess.run(["python", file_path])
            source_n_status["status"] = "success"
            source_n_status["traceback"] = None

        except Exception:
            source_n_status["status"] = "fail"
            source_n_status["traceback"] = traceback.format_exc()

        data_source_n_status.append(source_n_status)

    return spark, data_source_n_status


if __name__ == "__main__":
    run_etl(locals())
