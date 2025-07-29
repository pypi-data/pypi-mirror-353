# Databricks notebook source
import subprocess
import traceback
import os
import sys
from typing import Tuple

from pyspark.sql import SparkSession

from ETL.logging.logging_decorator_databricks_execute import log_databricks_execute
from ETL.logging.df_utils.logging_df_utils import db_name, DatabricksExecuteTable

from ETL.commons.start_spark_session import get_or_create_spark_session

log_table_class = DatabricksExecuteTable()


def get_files_to_execute(spark: SparkSession, sql_op: str):
    pwd = subprocess.check_output(["pwd"]).decode().strip()
    try:
        all_sql_files = [
            f"{pwd}/{sql_op}/{file}"
            for file in subprocess.check_output(["ls", sql_op]).decode().strip().split("\n")
        ]
    except Exception as e:
        print(e)
        all_sql_files = []
    executed_files = [row.script_path for row in spark.sql(f"select script_path from {log_table_class.table_name} where status = 'success';").collect()]
    files_to_execute = [path for path in all_sql_files if f"lakehouse/{path.split('/lakehouse/')[-1]}" not in executed_files]
    files_to_execute.sort()

    return files_to_execute


@log_databricks_execute(
    env=locals()
)
def run_etl(env: dict, sql_op: str) -> Tuple[SparkSession, list]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")
    spark.sql(f"create database if not exists {db_name};")
    spark.sql(log_table_class.create_table())

    file_paths = get_files_to_execute(spark, sql_op)

    if not file_paths:
        print(f"Exiting run: No {sql_op} files to execute...")
        return spark, []

    print(f"{len(file_paths)} files to process")
    data_source_n_status = []

    for file_path in file_paths:
        source_n_status = {"script_path": f"lakehouse/{file_path.split('/lakehouse/')[-1]}"}
        try:
            file_content = subprocess.check_output(["cat", file_path]).decode().strip()
            queries = [sql for sql in file_content.split(";") if sql.strip() != "" and sql.strip()[:2] != "--"]
            for query in queries:
                spark.sql(query)
            source_n_status["status"] = "success"
            source_n_status["traceback"] = None

        except Exception:
            source_n_status["status"] = "fail"
            source_n_status["traceback"] = traceback.format_exc()

        data_source_n_status.append(source_n_status)

    return spark, data_source_n_status


if __name__ == "__main__":
    sql_op = ""
    env = locals()
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        sql_op = env["getArgument"]("sql_op")
    else:
        if len(sys.argv) > 1:
            sql_op = sys.argv[1]

    if sql_op and sql_op in ["ddl", "dml", "dcl"]:
        run_etl(env, sql_op)
    else:
        print("Quitting ETL run.\nPlease provide a sql_op argument\nexpects: ddl, dml, or dcl")
