# Databricks notebook source
from typing import Tuple, Union

import os
import traceback
import time
from datetime import datetime
from pyspark.sql import SparkSession, functions as f

import ETL.scripts.ms_salesforce_sync.df_utils.ms_salesforce_sync_df_utils as df_utils
from ETL.scripts.ms_salesforce_sync.df_utils.commons import (
    get_filename_attr, read_csv_file, etl_steps, create_dataframe, create_csv_dataframe, reformat_df_data_field_types2
)
from ETL.commons.decrypt_encrypt_data import ms_datalake_connector_decryption
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.get_s3_filepaths import GetS3Files
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

start_date = datetime(2023, 12, 1).date().strftime("%Y/%m/%d")
end_date = datetime(2023, 12, 25).date().strftime("%Y/%m/%d")
overwrite = False
clear_all_tables = False
target_table_to_drop = None  # define string table name without database name

db_prefix = "data_science"
df_utils.db_name = f"{db_prefix}_{df_utils.db_name}" if df_utils.db_name[:12] != db_prefix else df_utils.db_name
db_name = df_utils.db_name
set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/all_ms_salesforce_sync.py"
processed_classes = []

exception_files = [
    "s3a://ytree-dl-landing-zone/landing/salesforce/ms-salesforce-sync/2023/07/11/lead_all.csv",
    "s3a://ytree-dl-landing-zone/landing/salesforce/ms-salesforce-sync/2023/07/12/lead_all.csv",
    "s3a://ytree-dl-landing-zone/landing/salesforce/ms-salesforce-sync/2023/07/13/lead_all.csv"
]


def get_source_files(env) -> Tuple[list, Union[list, str], float]:
    file_paths = []
    duration_s = 0.0
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        breadcrumb = "landing/salesforce/ms-salesforce-sync"
        get_filepaths = GetS3Files(env=env, breadcrumb=breadcrumb, date_range={"start": start_date, "end": end_date})
        paths = get_filepaths.file_paths
        duration_s = get_filepaths.duration_sec
        target_files = ["lead", "opportunity", "company", "account"]
        target_file_types = ["csv", "parquet"]
        file_paths = [
            path for path in paths
            if path.replace("_all.", ".").split("/")[-1].split(".")[0] in target_files and
               path.split(".")[-1] in target_file_types
        ] if isinstance(paths, list) else []
    else:
        paths = "running outside databricks"
        import glob
        target_dir = "/Users/muhammad-saeedfalowo/Documents/etl_files/ms_salesforce_sync_parquet"
        pattern = target_dir + '/*.parquet'
        file_paths = [path for path in glob.glob(pattern)]

    return file_paths, paths, duration_s


def load_exception_files(spark: SparkSession, table_class, file_path: str, overwrite: bool = True, file_content: str = ""):
    print(f"\nProcessing data file for Table: {table_class.table_name}\n")
    print(f"data source: {file_path}\n")
    # Create Spark DataFrame
    df = create_dataframe(spark, file_path) if not file_content else create_csv_dataframe(spark, file_content)
    file_arrival_date = "-".join(file_path.split("/")[-4:-1])
    df = df.withColumn("file_arrival_date", f.lit(file_arrival_date))
    # Reformat the df to cast the fields with the expected datatype as stated in the table spark schema
    df, schema_report = reformat_df_data_field_types2(df, table_class)
    table_schema = table_class.get_spark_schema()
    df.select(table_schema.names).write.format("delta").mode("overwrite" if overwrite else 'append').option("mergeSchema", "true").saveAsTable(table_class.table_name)

    return schema_report


@log_general_info(
    env=locals(),
    etl_data="data_science_ms_salesforce_sync",
    script_path=script_path,
    data_sources_type="datalake"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    spark.conf.set('spark.sql.caseSensitive', True)
    file_paths, paths, get_data_sources_duration_s = get_source_files(env)

    if not file_paths:
        print(f"Exiting run:\n{paths}")
        return spark, [], get_data_sources_duration_s

    print(f"Spark UI Url: {spark_ui_url}")

    if clear_all_tables:
        spark.sql(f"drop database if exists {db_name} cascade;")  # to drop the database along with all its tables
        time.sleep(5)

    if target_table_to_drop:
        spark.sql(f"drop table if exists {db_name}.{target_table_to_drop};")
        time.sleep(5)

    spark.sql(f"create database if not exists {db_name};")

    print(f"{len(file_paths)} files to process")
    data_source_n_status = []

    for file_path in file_paths:
        source_n_status = {"data_source": file_path}
        try:
            # Get file identifiers from filename
            class_name = get_filename_attr(file_path)
            if class_name in ["EventsTable", "ReferralsTable"]:
                class_name = class_name.replace("sTable", "Table")

            # Instantiate table class
            table_class = eval(f"df_utils.{class_name}()")

            file_content = ""
            if file_path.split(".")[-1] == "csv":
                # Decrypt Encrypted s3 files
                stripped_path = "/".join(file_path.split("/")[3:])
                file_content = read_csv_file(file_path)
                is_encrypted = True if file_content[:6] == "vault:" else False
                status_code = 200

                if is_encrypted:
                    status_code, file_content = ms_datalake_connector_decryption(env, stripped_path)

                if status_code != 200:
                    source_n_status["status"] = "fail"
                    source_n_status[
                        "traceback"] = f"decryption status_code: {status_code}\n\ndecryptioin string return: {file_content}"
                    continue

            global processed_classes
            overwrite_table = overwrite if class_name not in processed_classes else False
            if file_path not in exception_files:
                schema_report = etl_steps(spark, table_class, file_path, overwrite_table, file_content)
            else:
                schema_report = load_exception_files(spark, table_class, file_path, overwrite_table, file_content)

            processed_classes += [class_name] if class_name not in processed_classes else []
            print(f"wrote df into {table_class.table_name} table with overwrite: {overwrite_table}")

            if schema_report.has_fields_report():
                source_n_status["status"] = "warning"
                source_n_status["traceback"] = schema_report.generate_warning_msg()
            else:
                source_n_status["status"] = "success"
                source_n_status["traceback"] = None

        except Exception as e:
            source_n_status["status"] = "fail"
            source_n_status["traceback"] = traceback.format_exc()

        data_source_n_status.append(source_n_status)

    return spark, data_source_n_status, get_data_sources_duration_s


if __name__ == "__main__":
    run_etl(locals())
