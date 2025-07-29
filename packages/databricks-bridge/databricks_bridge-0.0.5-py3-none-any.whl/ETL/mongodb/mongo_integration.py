# Databricks notebook source
from typing import Tuple
import os
import traceback

from pyspark.sql.session import SparkSession
from pyspark.sql import DataFrame

from ETL.mongodb.df_utils.mongodb_df_utils import get_mongo_data_dict, get_views
from ETL.commons.sql_auto_explode import SQLAutoExplode
from ETL.commons.connect_databases import MongoDBConn
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info


set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/mongo_integration.py"
mongo_conn_class = MongoDBConn(env=locals())
mongo_tables_db_name = "mongodb"
views = get_views()


def read_mongo_collection_df(spark: SparkSession, mongo_uri: str, db_name: str, collection_name: str):
    return spark.read.format("mongo")\
        .option("spark.mongodb.input.uri", mongo_uri)\
        .option("database", db_name)\
        .option("collection", collection_name)\
        .option("partitioner", "MongoSinglePartitioner")\
        .option("spark.mongodb.input.uri", mongo_uri)\
        .load()


def write_df_as_table(spark: SparkSession, df: DataFrame, table_name: str):
    spark.sql(f"drop table if exists {table_name}")
    df.write.mode("overwrite").saveAsTable(table_name)
    print(f"Saved data as table: {table_name}\n")


def etl_steps(spark: SparkSession, db_name, collection_name, view_fcn):
    uri = mongo_conn_class.get_mongodb_connection_uri()
    df = read_mongo_collection_df(spark, uri, db_name, collection_name)

    if df.limit(1).count() == 0:
        warning_msg = f"No data found in the db={db_name}, collection={collection_name}"
        print(f"{warning_msg}\n ")
        return warning_msg

    table_name = f"{mongo_tables_db_name}.{db_name.replace('-', '_')}__{collection_name.replace('-', '_')}"
    write_df_as_table(spark, df, table_name)
    if view_fcn:
        sql_auto_class = SQLAutoExplode(src_table_name=table_name, src_table_schema=df.schema)
        spark.sql(view_fcn(src_select=sql_auto_class.select_query))
        print(f"view created: {table_name}_vw\n")
    return None


@log_general_info(
    env=locals(),
    etl_data="mongo_integration",
    script_path=script_path,
    data_sources_type="mongodb"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)

    data_source_n_status = []
    for el in get_mongo_data_dict():
        db_name = el["database"]
        collection_names = el["collections"]
        spark.sql(f"create database if not exists {mongo_tables_db_name};")

        for collection_name in collection_names:
            src = f"db={db_name}, collection={collection_name}"
            view_key = f"{db_name}.{collection_name}"
            view_fcn = views[view_key] if view_key in views.keys() else None
            logger_helper = LoggerHelper(source=src)
            print(f"Retrieving data for: {src}")
            try:
                warning_msg = etl_steps(spark, db_name, collection_name, view_fcn)
                if warning_msg:
                    logger_helper.log_status(traceback=warning_msg, warn=True)
                else:
                    logger_helper.log_status()
            except Exception as e:
                logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

            data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())
