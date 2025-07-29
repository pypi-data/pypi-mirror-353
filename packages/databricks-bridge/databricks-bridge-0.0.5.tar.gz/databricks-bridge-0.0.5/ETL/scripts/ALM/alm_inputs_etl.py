# Databricks notebook source
import json
from typing import Tuple
import os
import traceback
import time
from datetime import datetime

from pyspark.sql import SparkSession

from ETL.scripts.ALM.df_utils.alm_df_utils import *
from ETL.scripts.ALM.df_utils.common_fcns import (get_active_client_ids, alm_input_etl_steps, get_alm_input_data)
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.keycloak_service import get_token
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info


set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/alm_inputs_etl.py"


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="ms-alm"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    data_source_n_status = []

    start_time = datetime.now()
    client_ids = get_active_client_ids(spark)
    endpoint_targets = ["expenses", "alm/family", "gifting", "incomes", "savings", "alm/settings"]
    alm_input_dict_data = {}
    for target in endpoint_targets:
        keycloak_token = get_token(env)['access_token']
        logger_helper = LoggerHelper(source=f"{target}")
        alm_input_data = []
        try:
            if target == "alm/settings":
                alm_input_data = get_alm_input_data(env, keycloak_token, target)
                logger_helper.log_status()
            else:
                alm_input_data = get_alm_input_data(env, keycloak_token, target, client_ids)
                errors = [el for el in alm_input_data if "error" in el.keys()]
                alm_input_data = [el for el in alm_input_data if "error" not in el.keys()]
                if errors:
                    logger_helper.log_status(traceback=json.dumps(errors), failed=True)
                else:
                    logger_helper.log_status()
        except Exception as e:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

        if alm_input_data:
            alm_input_dict_data[target] = alm_input_data
        time.sleep(1)

    get_data_sources_duration_s = (datetime.now() - start_time).total_seconds()

    if not alm_input_dict_data:
        print("Exiting run:\n empty snapshots")
        return spark, [], get_data_sources_duration_s

    spark.sql(f"create database if not exists {db_name};")

    for endpoint_target, alm_data in alm_input_dict_data.items():

        batch_number = 1
        batch_increment = 1000
        overwrite_mode = True

        for indx in range(0, len(alm_data), batch_increment):
            batch_alm_response = alm_data[indx:indx + batch_increment]
            sources = [] if endpoint_target == "alm/settings" else [res["client_profile_id"] for res in batch_alm_response]
            logger_helper = LoggerHelper(source=sources)
            try:
                print(f"Batch {batch_number} - Reading '{endpoint_target}' endpoint responses to memory...")
                schema_reports = alm_input_etl_steps(spark, batch_alm_response, endpoint_target, overwrite_mode)
                end_indx = indx + batch_increment if indx + batch_increment < len(alm_data) else len(alm_data)
                print(
                    f"Wrote {indx}:{end_indx} data range of {len(alm_data)} into {endpoint_target} tables with {'overwrite' if overwrite_mode else 'append'} mode\n")

                batch_number += 1
                overwrite_mode = False
                logger_helper.log_status(schema_report=schema_reports)

            except Exception as e:
                logger_helper.log_status(traceback=traceback.format_exc(), failed=True)
                print(traceback.format_exc())

            data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, get_data_sources_duration_s


if __name__ == "__main__":
    run_etl(locals())
