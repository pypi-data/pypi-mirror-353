# Databricks notebook source
from typing import Tuple, Union
import os
import traceback
import json
import time
from datetime import datetime, date, timedelta

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
import pyspark.sql.functions as f

from ETL.scripts.survicate.df_utils.survicate_df_utils import *

from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.normalize_data import unnest_array_struct_df
from ETL.commons.api_requests import survicate_api_get_request
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info


set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/survicate_etl.py"

init_load = False

start_date = f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}.000000Z"
end_date = f"{(date.today() + timedelta(days=-1)).strftime('%Y-%m-%dT%H:%M:%S')}.000000Z"
table_classes = {
    "surveys": SurveysTable(),
    "questions": QuestionsTable(),
    "responses": ResponsesTable(),
    "respondent_attributes": RespondentAttributesTable()
}


def reformat_answers(dict_data):
    for i in range(len(dict_data["data"])):
        if "answers" in dict_data["data"][i].keys():
            for j in range(len(dict_data["data"][i]["answers"])):
                if "answer" in dict_data["data"][i]["answers"][j].keys():
                    if isinstance(dict_data["data"][i]["answers"][j]["answer"], str):
                        dict_data["data"][i]["answers"][j]["answer"] = {
                            "text": dict_data["data"][i]["answers"][j]["answer"]}
    return dict_data


def get_survicate_data(env: dict, id: str = None, req_data: str = None) -> Union[list, dict]:
    if not id:
        end_point = "/surveys"
    elif id and req_data == "questions":
        end_point = f"/surveys/{id}/questions"
    elif id and req_data == "responses":
        end_point = f"/surveys/{id}/responses"
        end_point += f"?start={start_date}&end={end_date}&items_per_page=20" if not init_load else ""
    elif id and req_data == "respondent_attributes":
        end_point = f"/respondents/{id}/attributes"
        # end_point += f"?start={start_date}&end={end_date}&items_per_page=20" if not init_load else ""
    else:
        print(f"req_data: {req_data}")

    def recur(_end_point: str, _payload: list):
        # print(f"retrieving survicate data from endpoint: {_end_point}")
        status_code, text = survicate_api_get_request(env, _end_point)
        dict_data = json.loads(text)
        dict_data = reformat_answers(dict_data) if req_data == "responses" else dict_data
        if status_code == 200:
            _payload += dict_data["data"]
            if dict_data["pagination_data"]["next_url"]:
                next_page_url = dict_data["pagination_data"]["next_url"]
                time.sleep(2)
                _payload = recur(next_page_url, _payload)

        return _payload

    return recur(end_point, [])


def reformat_respondents_attributes(dict_list: list) -> dict:
    dict_data = {}
    for el in dict_list:
        dict_data[el["name"]] = el["value"]

    return dict_data


def pop_empty_keys(missed_fields):
    empty_keys = [k for k, v in missed_fields.items() if not v]
    for key in empty_keys:
        missed_fields.pop(key)

    return missed_fields


def create_json_dataframe_from_dict_list(spark: SparkSession, dict_list: Union[list, dict]) -> DataFrame:
    # Load data into spark dataframe
    return spark.read.json(spark.sparkContext.parallelize([json.dumps(dict_list)]))


def rename_df_cols(df: DataFrame):
    for _col in df.columns:
        df = df.withColumnRenamed(_col, _col.replace("answers_", ""))
    return df


def filter_out_existing_rows(spark: SparkSession, df: DataFrame, table_class):
    unq_id = table_class.unq_id
    table_name = table_class.table_name
    df_ids_collect = df.select(unq_id).distinct().collect()
    ids_sql_str = ",".join([f"'{row[unq_id]}'" for row in df_ids_collect])
    existing_ids_collect = spark.sql(f"""
        select distinct {unq_id} from {table_name}
        where {unq_id} in ({ids_sql_str if ids_sql_str else ''});
    """).collect()
    existing_ids = ",".join([f"'{row[unq_id]}'" for row in existing_ids_collect])

    print(f"removing {len(existing_ids_collect)} ids from total {len(df_ids_collect)} unq ids in df to be inserted")
    return df.filter(f.expr(f"{unq_id} not in ({existing_ids})")) if existing_ids else df


def write_df_to_table(df: DataFrame, col_names: list, table_name: str, overwrite: bool = False):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite)


def process_survicate_data(spark: SparkSession, table_class, survey_data: Union[dict, list], survey_id: str = None):
    df = create_json_dataframe_from_dict_list(spark, survey_data)
    df = unnest_array_struct_df(df, table_class.nested_fields)
    df = df.withColumn("survey_id", f.lit(survey_id)) if survey_id else df
    df = rename_df_cols(df) if table_class == table_classes["responses"] else df
    df = df.withColumn("insert_timestamp", f.expr("current_timestamp"))
    df, schema_report = reformat_df_data_field_types2(df, table_class)
    df = filter_out_existing_rows(spark, df, table_class)

    return df, schema_report


def etl_steps(env: dict, spark: SparkSession, survey: dict):
    _table_class = table_classes["surveys"]
    df, schema_report_surveys = process_survicate_data(spark, _table_class, survey_data=survey)
    write_df_to_table(df, _table_class.get_spark_schema().names, _table_class.table_name)

    _table_class = table_classes["questions"]
    questions = get_survicate_data(env, id=survey["id"], req_data="questions")
    df, schema_report_questions = process_survicate_data(spark, _table_class, survey_data=questions, survey_id=survey["id"])
    write_df_to_table(df, _table_class.get_spark_schema().names, _table_class.table_name)

    _table_class = table_classes["responses"]
    responses = get_survicate_data(env, id=survey["id"], req_data="responses")
    if not responses:
        print(f"No responses for survey: {survey['id']}\n")
        return [schema_report_surveys, schema_report_questions]

    df, schema_reports_responses = process_survicate_data(spark, _table_class, survey_data=responses, survey_id=survey["id"])
    write_df_to_table(df, _table_class.get_spark_schema().names, _table_class.table_name)

    _table_class = table_classes["respondent_attributes"]
    respondents_uuid = [
        row.uuid for row in spark.sql("select distinct respondent_uuid uuid from survicate.responses").collect()
    ]
    respondent_attr = []
    for uuid in respondents_uuid:
        _respondent_attr_list = get_survicate_data(env, id=uuid, req_data="respondent_attributes")
        _respondent_attr_dict = reformat_respondents_attributes(_respondent_attr_list)
        _respondent_attr_dict["respondent_uuid"] = uuid
        respondent_attr.append(_respondent_attr_dict)

    df, schema_report_respondent_attributes = process_survicate_data(spark, _table_class, survey_data=respondent_attr)
    write_df_to_table(df, _table_class.get_spark_schema().names, _table_class.table_name)

    print(f"Processed responses for survey_id: {survey['id']}\n")
    return [schema_report_surveys, schema_report_questions, schema_report_respondent_attributes]


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="survicate.com"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    spark.sql(f"create database if not exists {db_name};")

    for k, v in table_classes.items():
        if init_load:
            spark.sql(v.delete_table())
            print(f"drop existing table {v.table_name}")

        spark.sql(v.create_table())

    data_source_n_status = []

    surveys_list = get_survicate_data(env)
    print(f"Processing {len(surveys_list)} surveys and its responses")
    for survey in surveys_list:
        logger_helper = LoggerHelper(source=f"survey_id: {survey['id']}")
        try:
            schema_reports = etl_steps(env, spark, survey)
            logger_helper.log_status(schema_report=schema_reports)

        except Exception as e:
            msg = f"Error on: \n{traceback.format_exc()}"
            logger_helper.log_status(traceback=msg, failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())
