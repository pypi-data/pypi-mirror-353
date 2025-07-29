# Databricks notebook source
from typing import Tuple
import os
import time
import traceback

from pyspark.sql import SparkSession

from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info
from ETL.RDS.rds_df_utils.rds_df_utils import RDSConfigTable

from databricks_execute.utils.cleanup_utils import get_table_list

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/delta_vacuum_cleanup.py"

thirty_days_exceptions = ["analytics", "ifls_investment_solution", "ifls", "cpd"]
full_db_vacuum = ["logging", "loaded", "cleansed", "client_holdings"]
exclusion_tables = [
    "logging.databricks_job_logs_history"
]


def get_rds_tables():
    table_list = [el["table_name"] for el in RDSConfigTable.get_rds_tables_dict()]

    return table_list


def get_database_tables(spark: SparkSession, db_name: str) -> list:
    df_tbl = spark.sql(f"show tables from {db_name}")
    df_vw = spark.sql(f"show views from {db_name}")
    df = df_tbl.join(df_vw.selectExpr("viewName as tableName"), "tableName", "anti")
    table_names = [f"{db_name}.{row.tableName}" for row in df.collect()]
    table_names = [el for el in table_names if el not in exclusion_tables]

    return table_names


def get_tables_from_databases(spark: SparkSession, db_names: list) -> list:
    table_names = []
    for _db in db_names:
        table_names += get_database_tables(spark, _db)

    return table_names


def get_vacuum_tables(spark: SparkSession) -> list:

    rds_tbl_names = get_rds_tables()

    remote_schemas = [row.databaseName for row in spark.sql("show databases").collect()]
    _full_db_vacuum = [_db for _db in full_db_vacuum if _db in remote_schemas]
    _thirty_days_exceptions = [_db for _db in thirty_days_exceptions if _db in remote_schemas]
    _other_schemas = [
        _db for _db in remote_schemas
        if _db not in _full_db_vacuum + _thirty_days_exceptions + list(set([el.split(".")[0] for el in rds_tbl_names]))
    ]

    vacuum_dict_list = [{
        "table_list": rds_tbl_names + get_tables_from_databases(spark, _full_db_vacuum),
        "retain": None
    }, {
        "table_list": get_tables_from_databases(spark, _thirty_days_exceptions),
        "retain": 720  # 720 hours == 30 days
    }, {
        "table_list": get_tables_from_databases(spark, _other_schemas),
        "retain": 720  # 720 hours == 30 days
    }]

    return vacuum_dict_list


@log_general_info(
    env=locals(),
    etl_data="delta_tables_vacuum_cleanup",
    script_path=script_path,
    data_sources_type="lakehouse"
)
def run_cleanup(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    vacuum_dict_list = get_vacuum_tables(spark)

    data_source_n_status = []
    total_tbl_cnt = sum([len(el["table_list"]) for el in vacuum_dict_list])

    cnt = 1
    for el in vacuum_dict_list:
        table_list = el["table_list"]
        rentention_hrs = el["retain"]

        for table_name in table_list:
            source_n_status = {"data_source": table_name}
            table_name = ".".join([f"`{el}`" for el in table_name.split(".")])

            try:
                vacuum_sql = f"vacuum {table_name}"
                vacuum_sql += f" retain {rentention_hrs} hours" if rentention_hrs else ""

                spark.sql(vacuum_sql)
                print_log = f"vacuum'ed table {cnt}/{total_tbl_cnt}: {table_name}"
                print_log += f" with {rentention_hrs} hours retention period" if rentention_hrs else ""
                print(print_log)
                cnt += 1
                # time.sleep(0.1)

                source_n_status["status"] = "success"
                source_n_status["traceback"] = None

            except Exception as e:
                source_n_status["status"] = "fail"
                source_n_status["traceback"] = f"Error while running 'vacuum' on {table_name}:\n{traceback.format_exc()}"

            data_source_n_status.append(source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_cleanup(locals())
