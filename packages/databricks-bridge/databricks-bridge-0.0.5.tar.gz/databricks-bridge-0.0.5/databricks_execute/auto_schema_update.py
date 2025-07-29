# Databricks notebook source
import shutil
import os
import traceback
from typing import Tuple

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame

from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.ease_of_use_fcns import get_checkpoint_dir
from ETL.logging.logging_decorator_databricks_execute import log_databricks_execute

from databricks_execute.utils.auto_schema_update_table_classes import TableClasses
from databricks_execute.utils.commons import switch_catalog, execute_dependant_queries, get_schema_field_datatype_names

table_classes = TableClasses().table_classes


def match_table_to_expected_schema(spark: SparkSession, table_class, temp_table_name, catalog: str):
    table_schema = table_class.get_spark_schema()
    df = spark.sql(f"select * from {table_class.table_name}")
    df_final, _ = reformat_df_data_field_types2(df, table_class)
    write_files_to_tables(df_final, table_schema.names, temp_table_name)


def confirm_and_update_target_table(spark: SparkSession, table_class, temp_table_name, drop_temp_table_query):
    new_table_df = spark.sql(f"select * from {temp_table_name}")
    table_schema = table_class.get_spark_schema()
    df_fields_and_types = get_schema_field_datatype_names(schema=new_table_df.schema)
    table_fields_and_types = get_schema_field_datatype_names(schema=table_schema)
    if table_schema == new_table_df.schema or df_fields_and_types == table_fields_and_types:
        # drop and recreate target table
        spark.sql(table_class.delete_table())
        spark.sql(table_class.create_table())
        write_files_to_tables(new_table_df, table_schema.names, table_class.table_name)

        # drop temp table
        spark.sql(drop_temp_table_query)
        print(f"{table_class.table_name} schema now matches expected schema\n")
    else:
        print(f"unable to confirm match {table_class.table_name} schema with expected schema\n")


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str):
    df.select(col_names).write.insertInto(table_name, overwrite=True)


def update_table_schema(spark: SparkSession, table_class, remote_tbl_df: DataFrame, catalog: str):
    # create temp table to work on
    temp_table_name = f"{table_class.table_name}_asu_temp"
    drop_temp_table_query = table_class.delete_table().replace(table_class.table_name, temp_table_name)
    create_temp_table_query = table_class.create_table().replace(table_class.table_name, temp_table_name)

    spark.sql(drop_temp_table_query)
    spark.sql(create_temp_table_query)

    # retype, add, and remove columns as expected
    match_table_to_expected_schema(spark, table_class, temp_table_name, catalog)
    confirm_and_update_target_table(spark, table_class, temp_table_name, drop_temp_table_query)


@log_databricks_execute(
    env=locals()
)
def main(env) -> Tuple[SparkSession, list]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    data_source_n_status = []
    class_srcs = []

    for table_class in table_classes:
        current_catalog = switch_catalog(spark, table_class)
        class_srcs = execute_dependant_queries(spark, table_class, class_srcs)
        table_name = table_class.table_name
        source_n_status = {"script_path": None}
        schema_update_target = f"table_name:{table_name}"
        try:
            table_schema = table_class.get_spark_schema()
            spark.sql(f"create database if not exists {table_name.split('.')[0]};")

            spark.sql(table_class.create_table())
            remote_tbl_df = spark.sql(f"select * from {table_name}")

            table_fields_and_types = get_schema_field_datatype_names(schema=table_schema)
            remote_tbl_fields_and_types = get_schema_field_datatype_names(schema=remote_tbl_df.schema)
            if table_fields_and_types != remote_tbl_fields_and_types:
                # if col names are the same, then its data type that is different
                update_table_schema(spark, table_class, remote_tbl_df, current_catalog)
            else:
                print(f"{table_name} schema is up-to-date\nskipping...\n")
    
            source_n_status["status"] = "success"
            source_n_status["traceback"] = schema_update_target

        except Exception:
            source_n_status["status"] = "fail"
            source_n_status["traceback"] = f"{schema_update_target} | {traceback.format_exc()}"

        data_source_n_status.append(source_n_status)

    return spark, data_source_n_status


if __name__ == "__main__":
    main(locals())
