
import subprocess
import traceback
import os
import sys
import requests
import json
from datetime import datetime
from typing import Tuple

from databricks import sql
from pyspark.sql import SparkSession
from pandas import DataFrame

from ETL.logging.logging_decorator_databricks_execute import log_databricks_execute
from ETL.logging.df_utils.logging_df_utils import db_name, DatabricksExecuteTable, QueryLogTable
from ETL.logging.query_logger import QueryLogger

from ETL.commons.start_spark_session import get_or_create_spark_session

log_table_class = DatabricksExecuteTable()


def retrieve_all_files(sql_op: str):
    pwd = subprocess.check_output(["pwd"]).decode().strip()
    try:
        all_sql_files = [
            f"{pwd}/{sql_op}/{file}"
            for file in subprocess.check_output(["ls", sql_op]).decode().strip().split("\n")
        ]
    except Exception as e:
        print(e)
        all_sql_files = []

    return all_sql_files


def get_files_to_execute(spark: SparkSession, log_table_name, all_sql_files: list):
    executed_files = [row.script_path for row in spark.sql(f"select script_path from {log_table_name} where status = 'success';").collect()]
    files_to_execute = [path for path in all_sql_files if f"lakehouse/{path.split('/lakehouse/')[-1]}" not in executed_files]
    files_to_execute.sort()

    return files_to_execute


def get_queries_to_execute(spark: SparkSession, query_log_table_name: str, queries: list, script_path: str):
    executed_queries = [row.query for row in spark.sql(f"select query from {query_log_table_name} where status = 'success' and script_path = '{script_path}';").collect()]
    hashified_executed_queries = [query.lower().replace(" ", "") for query in executed_queries]
    queries_to_execute = [query for query in queries if query.lower().replace(" ", "") not in hashified_executed_queries]
    print(f"{len(executed_queries)}/{len(queries)} has been previously executed")

    return queries_to_execute


def get_sql_endpoint_id(token, host_name) -> str:
    HEADERS = {
        "Authorization": f"Bearer {token}"
    }
    res = requests.get(url=f"https://{host_name}/api/2.0/preview/sql/data_sources", headers=HEADERS)
    sql_data_sources = json.loads(res.content.decode())
    sql_endpoint_id = [data_source["endpoint_id"] for data_source in sql_data_sources if data_source["name"] == "SQLEndpoint"][0]
    return sql_endpoint_id


def retrieve_sql_connection(env, spark):
    token = env["dbutils"].secrets.get(scope="databricks_execute_secrets", key="token")
    host_name = f'{spark.conf.get("spark.databricks.workspaceUrl").split(".")[0]}.cloud.databricks.com'
    sql_endpoint_id = get_sql_endpoint_id(token, host_name)
    print('got the token')
    connection = sql.connect(
        server_hostname=host_name,
        http_path=f"/sql/1.0/warehouses/{sql_endpoint_id}",
        access_token=token
    )
    print("connection established")
    return connection


def query_from_databricks(connection, query) -> DataFrame:
    cursor = connection.cursor()

    try:
        cursor.execute("use catalog hive_metastore;")
        cursor.execute(query)
        names = [x[0] for x in cursor.description]
        rows = cursor.fetchall()
        return DataFrame(rows, columns=names)

    finally:
        if cursor is not None:
            cursor.close()


def execute(env, sql_op):
    @log_databricks_execute(
        env=env
    )
    def run_etl(env: dict, sql_op: str) -> Tuple[SparkSession, list]:
        spark, sc, spark_ui_url = get_or_create_spark_session(env)
        print(f"Spark UI Url: {spark_ui_url}")
        spark.sql(f"create database if not exists {db_name};")
        spark.sql(log_table_class.create_table())
        connection = retrieve_sql_connection(env, spark)

        file_paths = get_files_to_execute(spark, log_table_class.table_name, retrieve_all_files(sql_op))

        if not file_paths:
            print(f"Exiting run: No {sql_op} files to execute...")
            return spark, []

        print(f"{len(file_paths)} files to process")
        data_source_n_status = []
        query_logger_class = QueryLogger(spark, "databricks_execute")

        for file_path in file_paths:
            script_path = f"lakehouse/{file_path.split('/lakehouse/')[-1]}"
            source_n_status = {"script_path": script_path}
            query_traceback = None
            try:
                file_content = subprocess.check_output(["cat", file_path]).decode().strip()
                queries = [sql for sql in file_content.split(";") if sql.strip() != "" and sql.strip()[:2] != "--"]
                queries = get_queries_to_execute(spark, QueryLogTable().table_name, queries, script_path)
                for query in queries:
                    start_time = datetime.now()
                    try:
                        df = query_from_databricks(connection, query)
                        query_logger_class.insert_log_into_table(
                            script_path=script_path, query=query,
                            success=True, start_time=start_time, end_time=datetime.now()
                        )
                    except Exception as e:
                        query_traceback = traceback.format_exc()
                        query_logger_class.insert_log_into_table(
                            script_path=script_path, query=query,
                            success=False, start_time=start_time, end_time=datetime.now()
                        )
                        print(e)
                        print(f"This query was failed during execution:\n{query}")
                        assert True == False

                source_n_status["status"] = "success"
                source_n_status["traceback"] = None

            except Exception:
                source_n_status["status"] = "fail"
                source_n_status["traceback"] = traceback.format_exc() if query_traceback is None else query_traceback

            data_source_n_status.append(source_n_status)

        return spark, data_source_n_status

    run_etl(env, sql_op)


"""
secret_scope employed for this sql_engine is: databricks_execute_secrets
REF: https://docs.databricks.com/security/secrets/secrets.html
"""
