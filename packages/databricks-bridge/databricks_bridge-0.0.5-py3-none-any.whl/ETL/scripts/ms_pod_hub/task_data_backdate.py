# Databricks notebook source
from typing import Tuple
import os
import humps
import traceback

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from ETL.scripts.ms_pod_hub.df_utils.task_data_df_utils import *
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/task_data_backdate.py"
table_class = TaskDataTable()


def get_source_files(env):
    breadcrumbs = ["landing/ms-pod-hub/TaskEvent"]
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs, date_range={"start": "2023/09/27", "end": "2023/10/23"})

    return file_helper


def remove_processed_files(spark: SparkSession, file_paths: list) -> list:
    query = table_class.unprocessed_files_filter_query(etl_data_name, file_paths)
    try:
        data_source_rdd = spark.sql(query).collect()
    except Exception as e:
        data_source_rdd = []
        print(e)

    if len(data_source_rdd) == 0:
        return file_paths
    else:
        processed_files = [row.data_source for row in data_source_rdd]
        unprocessed_files = [path for path in file_paths if path not in processed_files]
        print(f"{len(processed_files)}/{len(file_paths)} were already processed successfully so they have been removed")
        return unprocessed_files


def create_json_dataframe(spark: SparkSession, file_paths: list) -> DataFrame:
    # Load data into spark dataframe
    return spark.read.json(file_paths, multiLine=True)


def rename_df_cols(df: DataFrame) -> DataFrame:
    renamed_cols = [f"{_col} as {humps.decamelize(_col)}" for _col in df.columns]
    df = df.selectExpr(renamed_cols)
    return df


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str):
    df.select(col_names).write.insertInto(table_name, overwrite=False)


def split_files_by_date(file_paths: list) -> dict:
    files_dict = {}
    for path in file_paths:
        path_split = path.split("/")
        date_dict = {"year": path_split[-4], "month": path_split[-3], "day": path_split[-2]}
        file_date = f"{date_dict['year']}-{date_dict['month']}-{date_dict['day']}"
        if file_date in files_dict.keys():
            files_dict[file_date].append(path)
        else:
            files_dict[file_date] = [path]

    return files_dict


def etl_steps(spark: SparkSession, file_path: list) -> list:
    df = create_json_dataframe(spark, file_path)
    df = rename_df_cols(df)
    df_final, schema_report = reformat_df_data_field_types2(df, table_class)
    table_schema = table_class.get_spark_schema()
    task_ids = [row.id for row in df_final.select("id").collect()]
    table_class.delete_table_rows(task_ids)
    write_files_to_tables(df_final, table_schema.names, table_class.table_name)

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
    class_name = "TaskDataTable"
    file_per_date_dict = split_files_by_date(file_helper.file_paths)
    file_dates = list(file_per_date_dict.keys())
    file_dates.sort(reverse=False)  # sort in ascending order

    if not file_helper.file_paths:
        print("Exiting run:\n" + "\n".join(file_helper.get_s3_files_exceptions))
        return spark, [], file_helper.duration_s

    spark.sql(f"create database if not exists {db_name};")

    print(f"{len(file_helper.file_paths)} files to process")

    data_source_n_status = []
    spark.sql(table_class.create_table())
    spark.sql(f"create table if not exists {table_class.table_name}_bkp as select * from {table_class.table_name}")
    spark.sql(f"DELETE FROM {table_class.table_name}")
    failed_at_least_once = False
    for file_date in file_dates:
        batch_number = 1
        batch_increment = 1000
        overwrite_mode = False
        paths = file_per_date_dict[file_date]
        print(f"processing {len(paths)} files for file_date: {file_date}")

        for indx in range(0, len(paths), batch_increment):
            batch_paths = paths[indx:indx + batch_increment]
            logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
            try:
                print(f"Batch {batch_number} - Reading {class_name} data files data to memory...")
                schema_report = etl_steps(spark, batch_paths)
                end_indx = indx + batch_increment if indx + batch_increment < len(paths) else len(paths)
                print(
                    f"Wrote {indx}:{end_indx} data range of {len(paths)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")

                batch_number += 1

                logger_helper.log_status(schema_report=schema_report)

            except Exception as e:
                msg = f"Error on {class_name} data\n{traceback.format_exc()}"
                logger_helper.log_status(traceback=msg, failed=True)
                failed_at_least_once = True

            data_source_n_status.append(logger_helper.source_n_status)

    if not failed_at_least_once:
        spark.sql(f"drop table if exists {table_class.table_name}_bkp;")
        print(f"Dropped the {table_class.table_name}_bkp backup table")
    else:
        print(
            f"There was at least one failure during the backdate run, the backup table still exists in {table_class.table_name}_bkp ")

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
