# Databricks notebook source
from typing import Tuple, Union
import os
import json
import traceback
import datetime as dt
import boto3

from pyspark.sql import SparkSession, functions as f
from pyspark.sql.dataframe import DataFrame, SparkContext

from ETL.scripts.mixpanel.df_utils.mixpanel_raw_api_event_df_utils import (
    RawServiceAccountExportTable, RawEventsExportTable, db_name
)
from ETL.commons.api_requests import mixpanel_api_service_acc_request, mixpanel_api_event_export_request
from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.commons.unittest_utils import create_tempfile_from_string_data
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/mixpanel_raw_api_event_etl.py"
etl_data_name = "mixpanel_api_events"

init_load = False
time_now = dt.datetime.now()
# To ensure all previous day data is retrieved, the 1am scheduled run will query for previous day's data
# the other 6am and 12pm scheduled runs will query for current day's data
data_time = time_now if time_now.hour > 3 else time_now + dt.timedelta(days=-1)
current_datetime = data_time.strftime("%Y-%m-%d %H:%M:%S")
current_date = current_datetime.split(" ")[0]
from_date = "2023-01-01" if init_load else current_date

s3 = boto3.resource('s3', region_name="eu-west-2")
bucket_name = os.environ.get('BUCKET')

table_classes = {
    "service_acc_request": RawServiceAccountExportTable(),
    "event_export_request": RawEventsExportTable(),
}
call_time_col_name = "api_call_time"


def create_json_dataframe(spark: SparkSession, sc: SparkContext, dict_list: list) -> DataFrame:
    # Load data into spark dataframe
    return spark.read.json(sc.parallelize([json.dumps(dict_list)]))


def write_files_to_tables(df: DataFrame, table_name: str, col_names: list, overwrite_mode: bool = False):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite_mode)
    print(f"written data to {table_name} table with {'overwrite' if overwrite_mode else 'append'}...")


def write_data_to_s3(payload: Union[dict, list], table_name: str, file_name: str, project_id: str = None):
    _date = current_date.replace("-", "/")
    project_id_n_date = _date if not project_id else f"project_id={project_id}/{_date}"
    s3_path = f'landing/mixpanel/raw_api_export/{table_name}/{project_id_n_date}/{file_name}.json'
    object = s3.Object(bucket_name, s3_path)
    object.put(Body=json.dumps(payload).encode())
    print(f"uploaded to {s3_path}")


def preprocess_data_to_df(spark: SparkSession, sc: SparkContext, data: Union[dict, list], table_class, file_name: str):
    df = create_json_dataframe(spark, sc, data)
    df = df.withColumn("file_name", f.lit(file_name))
    if call_time_col_name in df.columns:
        df = df.withColumn(call_time_col_name, f.expr(f"cast({call_time_col_name} as timestamp)"))
    df, schema_report = reformat_df_data_field_types2(df, table_class)

    return df, schema_report


def generate_start_end_month_dates(_from_date: str, _current_date: str):
    date_ranges = []
    start_date = dt.datetime.strptime(_from_date, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(_current_date, "%Y-%m-%d").date()
    year_range = [el for el in range(start_date.year, end_date.year)] + [end_date.year]
    for year in year_range:
        for month in range(1, 13):
            dt.date(year, month, 1).strftime("%Y-%m-%d")
            _start = dt.date(year, month, 1).strftime("%Y-%m-%d")
            _end = (dt.date(year+1 if month == 12 else year, 1 if month == 12 else month+1, 1) + dt.timedelta(days=-1)).strftime("%Y-%m-%d")
            _end = end_date.strftime("%Y-%m-%d") if dt.datetime.strptime(_end, "%Y-%m-%d").date() > end_date else _end

            date_ranges.append({"start": _start, "end": _end})
            if _end == _current_date:
                break

    return date_ranges


def etl_steps(env: dict, spark: SparkSession, sc: SparkContext, table_class, project_ids: list):
    spark.sql(table_class.create_table())
    table_name = table_class.table_name.split(".")[-1]
    table_schema = table_class.get_spark_schema()
    schema_reports = []

    if not project_ids:
        api_call_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        code, text = mixpanel_api_service_acc_request(env)
        data = json.loads(text)
        data["api_call_time"] = api_call_time
        project_ids = list(data["results"]["projects"].keys())

        file_name = current_date
        df, _schema_report = preprocess_data_to_df(spark, sc, data, table_class, file_name)
        if _schema_report.has_fields_report():
            schema_reports.append(_schema_report)

        spark.sql(table_class.delete_rows(file_name))
        write_data_to_s3(data, table_name, file_name)
        write_files_to_tables(df, table_class.table_name, table_schema.names, True)
        spark.sql(table_class.create_view())

    else:
        date_ranges = []
        overwrite = False
        if not init_load:
            date_ranges.append({"start": current_date, "end": current_date})
        else:
            date_ranges += generate_start_end_month_dates(from_date, current_date)
            overwrite = True

        for id in project_ids:
            for date_range in date_ranges:
                _start_date = date_range["start"]
                _end_date = date_range["end"]
                file_name = f"start={_start_date}_end={_end_date}"

                data = []
                PARAMS = {"project_id": id, "from_date": _start_date, "to_date": _end_date}
                code, text = mixpanel_api_event_export_request(env, PARAMS)
                temp_file_path = create_tempfile_from_string_data(text.encode(), env)

                with open(temp_file_path) as file:
                    for line in file:
                        data.append(json.loads(line))

                df, _schema_report = preprocess_data_to_df(spark, sc, data, table_class, file_name)
                if _schema_report.has_fields_report():
                    schema_reports.append(_schema_report)

                spark.sql(table_class.delete_rows(file_name))
                write_data_to_s3(data, table_name, file_name, str(id))
                write_files_to_tables(df, table_class.table_name, table_schema.names, overwrite)
                overwrite = False

                # create normalised view of the events table data
                df_collect = spark.sql(table_class.unq_properties_query).collect()
                spark.sql(table_class.create_view(df_collect))
                spark.sql(table_class.create_view(df_collect, target_data="alm"))

    return project_ids, schema_reports


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="mixpanel_api"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    spark.sql(f"create database if not exists {db_name}")

    project_ids = []
    data_source_n_status = []

    for key, table_class in table_classes.items():
        logger_helper = LoggerHelper(source=f"{key} api call")
        class_name = table_class.__class__.__name__
        print(f"\nProcessing for {key} data...")
        try:
            project_ids, schema_reports = etl_steps(env, spark, sc, table_class, project_ids)
            logger_helper.log_status(schema_report=schema_reports)

        except Exception as e:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())
