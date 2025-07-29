# Databricks notebook source
from typing import Tuple
import os
import json
import humps
import traceback
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame, SparkContext

from ETL.commons.reformat_data import df_targeted_explosion, reformat_df_data_field_types2
from ETL.scripts.mixpanel.df_utils.segment_events_df_utils import *
from ETL.commons.decrypt_encrypt_data import ms_datalake_connector_decryption
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info
from ETL.logging.df_utils.logging_df_utils import GeneralInfoTable

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/segment_event_etl.py"
etl_data_name = "segment_events"


def get_source_files(env):
    file_helper = GetBreadcrumbFilesHelper(env, breadcrumbs="landing/ms_segment", date_diff=-1)

    return file_helper


def remove_processed_files(spark: SparkSession, file_paths: list, table_class) -> list:
    data_source_rdd = spark.sql(table_class.unprocessed_files_filter_query(etl_data_name, file_paths, GeneralInfoTable().table_name)).collect()
    if len(data_source_rdd) == 0:
        return file_paths
    else:
        processed_files = [row.data_source for row in data_source_rdd]
        unprocessed_files = [path for path in file_paths if path not in processed_files]
        print(f"{len(processed_files)}/{len(file_paths)} were already processed successfully so they have been removed")
        return unprocessed_files


def create_json_dataframe(spark: SparkSession, sc: SparkContext, dict_list: list) -> DataFrame:
    # Load data into spark dataframe
    return spark.read.json(sc.parallelize([json.dumps(dict_list)]))


def rename_df_cols(df: DataFrame, table_class) -> DataFrame:
    exploded_col_names = [
        {"cur_col_name": f"{k}_{el.replace('.', '')}", "new_col_name": f"{k}_{el.replace('.', '_')}"}
        for k, v in table_class.explodables.items() for el in v
    ]
    for el in exploded_col_names:
        df = df.withColumnRenamed(el["cur_col_name"], el["new_col_name"])

    for col in df.columns:
        df = df.withColumnRenamed(col, humps.decamelize(col).replace("__", "_"))

    return df


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str, overwrite_mode: bool):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite_mode)


def etl_steps(spark: SparkSession, sc: SparkContext, env: dict, table_class, batch_paths: list, overwrite_mode: bool) -> list:
    start_time = datetime.now()

    read_data = []
    for path in batch_paths:
        stripped_path = "/".join(path.split("/")[3:])
        status_code, file_content = ms_datalake_connector_decryption(env, stripped_path)
        data = json.loads(file_content) if status_code == 200 else []
        read_data += data if isinstance(data, list) else [data]

    if not read_data:
        print(f"status_code: {status_code}\nresponse: {file_content}")

    print(f"Done! Duration: {(datetime.now() - start_time).total_seconds()} seconds")

    print(f"Writing data into dataframes...")
    start_time = datetime.now()

    df = create_json_dataframe(spark, sc, read_data)
    df = df_targeted_explosion(df, table_class.explodables) if df.count() > 0 else df
    df = rename_df_cols(df, table_class)

    df_final, schema_report = reformat_df_data_field_types2(df, table_class)

    table_schema = table_class.get_spark_schema()
    write_files_to_tables(df_final, table_schema.names, table_class.table_name, overwrite_mode)

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

    table_class = EventsTable()
    if file_helper.file_paths:
        file_helper.file_paths = remove_processed_files(spark, file_helper.file_paths, table_class)

    if not file_helper.file_paths:
        print("Exiting run:\n" + "\n".join(file_helper.get_s3_files_exceptions))
        return spark, [], file_helper.duration_s

    spark.sql(f"create database if not exists {db_name};")
    spark.sql(table_class.create_table())

    print(f"{len(file_helper.file_paths)} files to process")

    data_source_n_status = []

    batch_number = 1
    batch_increment = 1000
    overwrite_mode = False

    for indx in range(0, len(file_helper.file_paths), batch_increment):
        batch_paths = file_helper.file_paths[indx:indx + batch_increment]
        logger_helper = LoggerHelper(source=batch_paths, path_n_sizes=file_helper.paths_n_sizes)
        try:
            print(f"Batch {batch_number} - Reading SegmentEvents data files data to memory...")
            schema_report = etl_steps(spark, sc, env, table_class, batch_paths, overwrite_mode)
            end_indx = indx + batch_increment if indx + batch_increment < len(file_helper.file_paths) else len(file_helper.file_paths)
            print(f"Wrote {indx}:{end_indx} data range of {len(file_helper.file_paths)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")
            # overwrite_mode = False
            batch_number += 1

            logger_helper.log_status(schema_report=schema_report)

        except Exception as e:
            msg = f"Error on Events data\n{traceback.format_exc()}"
            logger_helper.log_status(traceback=msg, failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, file_helper.duration_s


if __name__ == "__main__":
    run_etl(locals())
