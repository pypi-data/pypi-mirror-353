# Databricks notebook source
from typing import Tuple
import os
import traceback

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame

from ETL.scripts.ms_tax.df_utils.ms_tax_df_utils import *

from ETL.commons.reformat_data import (
    reformat_df_data_field_types2, add_file_path_df, add_file_arrival_date_df, drop_file_path_col_df, rename_df_cols
)
from ETL.commons.normalize_data import unnest_array_struct_df
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper, create_batch_files_json_dataframe
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info


set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/ms_tax_etl.py"

table_class = PensionTaxAllowanceTable()


def get_source_files(env):
    breadcrumbs = ["landing/ms_tax/pension/PENSION_TAX_ALLOWANCE_SNAPSHOT"]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs)

    return file_helper


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str, overwrite: bool = False):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite)


def etl_steps(spark: SparkSession, batch_paths: list, overwrite_mode: bool) -> list:
    df = create_batch_files_json_dataframe(spark, batch_paths)
    df = add_file_path_df(df)
    df = add_file_arrival_date_df(df)
    df = unnest_array_struct_df(df, table_class.explodables, unappendable_parent_keys)
    df = drop_file_path_col_df(df)
    df = rename_df_cols(df)
    df, schema_report = reformat_df_data_field_types2(df, table_class)
    spark.sql(table_class.create_table())
    table_schema = table_class.get_spark_schema()
    write_files_to_tables(df, table_schema.names, table_class.table_name, overwrite_mode)

    return schema_report


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")
    file_helper = get_source_files(env)

    if not file_helper.file_paths:
        print("Exiting run:\n" + "\n".join(file_helper.get_s3_files_exceptions))
        return spark, [], file_helper.duration_s

    print(f"{len(file_helper.file_paths)} files to process")

    spark.sql(f"create database if not exists {db_name};")
    data_source_n_status = []

    class_name = table_class.__class__.__name__

    batch_number = 1
    batch_increment = 1000
    overwrite_mode = True

    for indx in range(0, len(file_helper.file_paths), batch_increment):
        batch_paths = file_helper.file_paths[indx:indx + batch_increment]
        logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
        try:
            print(f"Batch {batch_number} - Reading {class_name} data files data to memory...")
            schema_report = etl_steps(spark, batch_paths, overwrite_mode)
            end_indx = indx + batch_increment if indx + batch_increment < len(file_helper.file_paths) else len(file_helper.file_paths)
            print(
                f"Wrote {indx}:{end_indx} data range of {len(file_helper.file_paths)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")

            batch_number += 1
            logger_helper.log_status(schema_report=schema_report)
            overwrite_mode = False

        except Exception as e:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
