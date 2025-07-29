# Databricks notebook source
from typing import Tuple, List, Text
import os
# import json
# from pyspark.sql.functions import lit
import boto3

import traceback
import requests
import time
from datetime import datetime, date
from pyspark.sql import SparkSession

from ETL.commons.api_requests import get_ms_kube_gateway_url
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.keycloak_service import get_token
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/client_holdings_etl.py"
etl_data_name = "client_holdings"
schema_name = "client_holdings"


def get_ids(spark) -> List:
    # get a list of active y-tree clients

    query = """
        select distinct y_tree_bo_id, activation_date from salesforce.account_all where y_tree_bo_id is not null 
        and stage == 'Client' and internal_user_profile is false
    """
    df = spark.sql(query)
    dfs = df.collect()
    ids = []
    for id in dfs:
        ids.append(id[0:2])

    return ids


def ms_financialdata_connector(client_id: str, start_date: str, end_date: str, token: str, env: dict) -> Text:
    # send an api request to ms-financialdata endpoint
    getway_url = get_ms_kube_gateway_url(env)
    URL = f"{getway_url}/v1/ms-financialdata/cpd/statement-row-details/search"
    PARAMS = {
      "clientId": client_id,
      "reportingCurrency": 840,
      "startDate": start_date,
      "endDate": end_date
    }
    HEADERS = {
        "Authorization": f"Bearer {token}"

    }
    res = requests.post(url=URL, json=PARAMS, headers=HEADERS)
    return res.text


def retrieve_historic_data(ids: list, token: str, env: dict) -> Tuple:
    # get client data

    start_time = datetime.now()
    today = str(date.today())
    i = 1
    client_holdings_historical_list = []
    for client_data in ids:
        client_id = client_data[0]
        start_date = client_data[1]

        historic = ms_financialdata_connector(client_id, start_date, today, token, env)
        client_holdings_historical_list.append({"client_id": client_id, "uploaded_date": today, "data": historic})

        save_to_s3(client_id, historic)

        i += 1
        if i % 10 == 0:
            time.sleep(3)
            print(i)

    # Calculate execution duration
    end_time = datetime.now()
    datetime_diff = end_time - start_time
    duration_s = datetime_diff.total_seconds()

    return client_holdings_historical_list, duration_s


def save_to_s3(client_id, historic):
    bucket = os.environ.get('BUCKET')
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    filename = f"landing/client_holdings/historic/{year}/{month}/{day}/{client_id}.json"
    s3 = boto3.client('s3')
    text_object = historic
    s3.put_object(
        Body=text_object,
        Bucket=bucket,
        Key=filename
    )

####### No longer required to write to a table but kept functions in case this change needs to be reverted#######

# def get_df_list(spark, sc, client_list) -> Tuple:
#     # cleaning and preparing the data in client_list

#     df_list = []
#     error_list = []
#     for i in range(len(client_list)):
#         try:
#             json_object = client_list[i]['data'] if isinstance(client_list[i]['data'], dict) else json.loads(
#                 client_list[i]['data'])
#             valid_client_data = client_list[i]
#             valid_client_data['data'] = json_object['items']

#             items_list = json_object['items']
#             mini_batch_increment = 50000
#             for indx in range(0, len(items_list), mini_batch_increment):
#                 batch_json_objects = items_list[indx:indx + mini_batch_increment]
#                 df_items = spark.read.json(sc.parallelize([json.dumps(batch_json_objects)]))
#                 df_items = df_items.withColumn('client_id', lit(client_list[i]['client_id']))
#                 df_items = df_items.withColumn('uploaded_date', lit(client_list[i]['uploaded_date']))
#                 str_select = [f"cast({col} as string) as {col}" for col in df_items.columns]
#                 df_items = df_items.selectExpr(str_select)
#                 colnames = df_items.columns
#                 colnames.sort()
#                 if df_items.count() > 0:
#                     df_list.append(df_items.select(colnames))
#                 else:
#                     error_list.append({"client_id": client_list[i]['client_id'], "error": "data is empty"})
#                 end_indx = indx + mini_batch_increment if indx + mini_batch_increment < len(
#                     items_list) else len(items_list)
#                 print(
#                     f"Read DF with index range of {indx}:{end_indx} from total data of  {len(items_list)} \n")

#         except Exception as e:
#             error_list.append({"client_id": client_list[i]['client_id'], "error": traceback.format_exc()})
#     return df_list, error_list
# def create_historic_table(spark, df_list):
#     table_name = "history"
#     # spark.sql(f"drop table if exists {schema_name}.{table_name}")
#     for _df in df_list:
#         colnames = _df.columns
#         colnames.sort()
#         _df.select(colnames)\
#         .write\
#         .format('delta' if os.environ.get('ISDATABRICKS', 'local') == "TRUE" else 'parquet')\
#         .mode('append')\
#         .option('mergeSchema', 'true')\
#         .saveAsTable(f"{schema_name}.{table_name}")
# def create_current_table(spark):
#     query = '''
#             WITH cte AS(
#             SELECT 
#             *, 
#             row_number() OVER (PARTITION BY client_id ORDER BY date DESC) RN 
#             FROM client_holdings.history)
#             SELECT * FROM cte WHERE RN = 1
#             '''
#     sql_current = spark.sql(query)
#     table_name = "current"
#     sql_current.write.mode('overwrite').option('overwriteSchema', 'true').saveAsTable(f"{schema_name}.{table_name}")


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="ms-financialdata"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    ids = get_ids(spark)

    if not ids:
        print("Exiting run:\n empty ids")
        return spark, [], 0.0

    spark.sql(f"create database if not exists {schema_name};")
    print(f"{len(ids)} clients to process")

    data_source_n_status = []
    logger_helper = LoggerHelper(source="ms-financialdata/cpd/statement-row-details")

    batch_number = 1
    batch_increment = 10
    get_data_sources_duration_s = 0.0
    batch_id_count = 0

    try:
        for indx in range(0, len(ids), batch_increment):
            batch_ids = ids[indx:indx + batch_increment]

            print(f"Batch {batch_number} - Reading client holdings data to memory...")

            keycloak_token = get_token(env)['access_token']
            historic, duration_s = retrieve_historic_data(batch_ids, keycloak_token, env)
            get_data_sources_duration_s += duration_s
            batch_number += 1
            batch_id_count += len(batch_ids) 

        print(f"{batch_id_count} files saved in S3 bucket")
        logger_helper.log_status()
    except Exception:
        logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

    data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, get_data_sources_duration_s


if __name__ == "__main__":
    run_etl(locals())