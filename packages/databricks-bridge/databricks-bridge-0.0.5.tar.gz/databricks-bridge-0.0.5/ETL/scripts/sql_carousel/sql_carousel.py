# Databricks notebook source
from typing import Tuple

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
import traceback
import os
import sys

from ETL.scripts.sql_carousel.df_utils.sql_carousel_df_utils import db_names, checkpoint_dir, InstantiateTableClasses
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.commons.ease_of_use_fcns import delete_checkpoint_dir
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/sql_carousel.py"


def create_sql_query_df(spark: SparkSession, sql_query: str) -> DataFrame:
    return spark.sql(sql_query).checkpoint()


def write_files_to_tables(df: DataFrame, table_name: str, overwrite_mode: bool):
    # df.write.insertInto(table_name, overwrite=overwrite_mode).option("overwriteSchema", "True")
    df.write.mode('overwrite').option("overwriteSchema", "true").saveAsTable(table_name)


@log_general_info(
    env=locals(),
    etl_data="sql_carousel",
    script_path=script_path,
    data_sources_type="lakehouse"
)
def run_etl(env: dict, schedule: str) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    spark.sparkContext.setCheckpointDir(checkpoint_dir)

    print(f"Spark UI Url: {spark_ui_url}")
    for k, v in db_names.items():
        spark.sql(f"create database if not exists {v};")

    data_source_n_status = []
    data_collected = {}

    table_classes = [sql_class for sql_class in InstantiateTableClasses().instantiate if sql_class.class_name == class_name]
    print("SQL classes to be executed:\n"+"\n".join([tbl_class.class_name for tbl_class in table_classes]))
    for table_class in table_classes:
        # Create table is not exist and insert dataframe into table
        spark.sql(table_class.create_table())
        print(f"\nExecuting {table_class.class_name}...")

        logger_helper = LoggerHelper(source=table_class.source_tables)
        try:
            for query in table_class.prep_queries:
                spark.sql(query)
            query_df = create_sql_query_df(spark, table_class.sql_query)
            logger_helper.log_status()

            print("Writing files data to tables...")
            write_files_to_tables(query_df, table_class.table_name, table_class.overwrite)

        except Exception:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    delete_checkpoint_dir(env, checkpoint_dir)
    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    class_name = ""
    env = locals()
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        class_name = env["getArgument"]("class_name")
    else:
        if len(sys.argv) > 1:
            class_name = sys.argv[1]

    if class_name:
        run_etl(env, class_name)
    else:
        print("Quitting ETL run.\nPlease provide a class_name argument")
