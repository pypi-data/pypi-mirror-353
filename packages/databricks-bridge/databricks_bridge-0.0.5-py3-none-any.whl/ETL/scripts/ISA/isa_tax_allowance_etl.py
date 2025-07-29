# Databricks notebook source
from typing import Tuple
import os
import json
import humps
import traceback
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame, SparkContext
from pyspark.sql import functions as f

from ETL.scripts.ISA.df_utils.isa_tax_allowance_df_utils import *
from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.decrypt_encrypt_data import ms_datalake_connector_decryption
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/isa_tax_allowance_etl.py"
etl_data_name = "isa_tax_allowance"

table_class = IsaTaxAllowanceSnapshotTable()
table_class_his = IsaTaxAllowanceSnapshotTable("historical")
class_name = table_class.__class__.__name__


def get_source_files(env):
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs="landing/isa_tax_allowance/ISA_TAX_ALLOWANCE_SNAPSHOT")

    return file_helper


def create_json_dataframe(spark: SparkSession, sc: SparkContext, dict_list: list) -> DataFrame:
    # Load data into spark dataframe
    return spark.read.json(sc.parallelize([json.dumps(dict_list)]))


def explode_df_array_column(df: DataFrame, col_name: str):
    df_filt = df.filter(f"{col_name} is not null")
    if df_filt.count() == 0 or col_name not in df_filt.columns:
        return df
    return df.withColumn(col_name, f.expr(f"explode_outer({col_name}) as {col_name}"))


def explode_df_struct_column(df: DataFrame, col_name: str):
    df_filt = df.filter(f"{col_name} is not null")
    if df_filt.count() == 0 or col_name not in df_filt.columns:
        return df
    nested_col_names = df.select(f"{col_name}.*").columns
    new_col_names = ["*"] + [f"{col_name}.{_c} as {col_name.replace('.', '_')}_{_c}" for _c in nested_col_names]

    new_df = df.selectExpr(new_col_names).drop(col_name)
    return new_df


def rename_df_cols(df: DataFrame) -> DataFrame:
    for col in df.columns:
        df = df.withColumnRenamed(col, humps.decamelize(col).replace("__", "_"))

    return df


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str, overwrite_mode: bool = False):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite_mode)


def etl_steps(spark: SparkSession, sc: SparkContext, env: dict, batch_paths: list, overwrite_mode: bool) -> list:
    start_time = datetime.now()

    read_data = []
    status_code = None
    file_content = None
    for path in batch_paths:
        stripped_path = "/".join(path.split("/")[3:])
        status_code, file_content = ms_datalake_connector_decryption(env, stripped_path)
        data = json.loads(file_content) if status_code == 200 else []
        read_data += data if isinstance(data, list) else [data]

    if not read_data:
        print(f"status_code: {status_code}\nresponse: {file_content}")

    print(f"Done reading {len(batch_paths)} files! Duration: {(datetime.now() - start_time).total_seconds()} seconds")
    print(f"Writing data into dataframes...")
    start_time = datetime.now()

    df = create_json_dataframe(spark, sc, read_data)
    df.cache()
    df = explode_df_array_column(df, col_name="taxPeriods")
    df = explode_df_struct_column(df, col_name="taxPeriods")
    df = explode_df_array_column(df, col_name="taxPeriods_taxUtilisation")
    df = explode_df_struct_column(df, col_name="taxPeriods_taxUtilisation")
    df = rename_df_cols(df)
    df = df.withColumn("insert_timestamp", f.lit(datetime.now()))

    df_final, schema_report = reformat_df_data_field_types2(df, table_class)

    table_schema = table_class.get_spark_schema()
    write_files_to_tables(df_final, table_schema.names, table_class.table_name, overwrite_mode)
    write_files_to_tables(df_final, table_schema.names, table_class_his.table_name)

    print(f"Done! Duration: {(datetime.now() - start_time).total_seconds()} seconds")

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

    spark.sql(f"create database if not exists {db_name};")
    spark.sql(table_class.create_table())
    spark.sql(table_class_his.create_table())

    print(f"{len(file_helper.file_paths)} files to process")

    data_source_n_status = []

    batch_number = 1
    batch_increment = 500
    overwrite_mode = True

    for indx in range(0, len(file_helper.file_paths), batch_increment):
        batch_paths = file_helper.file_paths[indx:indx + batch_increment]
        logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
        try:
            print(f"Batch {batch_number} - Reading {class_name} data files data to memory...")
            schema_report = etl_steps(spark, sc, env, batch_paths, overwrite_mode)
            end_indx = indx + batch_increment if indx + batch_increment < len(file_helper.file_paths) else len(file_helper.file_paths)
            print(f"Wrote {indx}:{end_indx} data range of {len(file_helper.file_paths)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")
            overwrite_mode = False
            batch_number += 1

            logger_helper.log_status(schema_report=schema_report)

        except Exception as e:
            msg = f"Error on {class_name} data\n{traceback.format_exc()}"
            logger_helper.log_status(traceback=msg, failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
