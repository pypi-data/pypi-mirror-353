# Databricks notebook source
import json
from typing import Tuple
import os
import traceback
import time
from datetime import datetime

from pyspark.sql import SparkSession
from ETL.scripts.ALM.df_utils.alm_df_utils import *
from ETL.scripts.ALM.df_utils.common_fcns import (
    snapshot_etl_steps, get_active_client_ids, get_all_snapshots, get_all_endpoint_snapshot_data,
    get_latest_completed_snapshots, consolidate_lifestrategy_snapshots
)
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.keycloak_service import get_token
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info


set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/alm_initial_snapshot.py"


@log_general_info(
    env=locals(),
    etl_data=etl_data_name,
    script_path=script_path,
    data_sources_type="ms-life-strategy"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")
    class_name = "AlmOutDataTable"
    table_class = AlmOutDataTable("updated")

    start_time = datetime.now()
    client_ids = get_active_client_ids(spark)
    keycloak_token = get_token(env)['access_token']
    time.sleep(1)
    all_snapshots = get_all_snapshots(env, client_ids, keycloak_token)
    time.sleep(1)
    completed_snapshots = get_latest_completed_snapshots(spark, all_snapshots)

    modelling_snapshots = get_all_endpoint_snapshot_data(env, keycloak_token, completed_snapshots, snap_target="modelling")
    time.sleep(1)
    incomes_snapshots = get_all_endpoint_snapshot_data(env, keycloak_token, completed_snapshots, snap_target="incomes")
    time.sleep(1)
    expenses_snapshots = get_all_endpoint_snapshot_data(env, keycloak_token, completed_snapshots, snap_target="expenses")
    time.sleep(1)
    wealth_by_wrapper_snapshots = get_all_endpoint_snapshot_data(env, keycloak_token, completed_snapshots, snap_target="lifetime-wealth")
    time.sleep(1)

    snapshots_consolidated = consolidate_lifestrategy_snapshots(
        completed_snapshots,
        modelling_snapshots,
        incomes_snapshots,
        expenses_snapshots,
        wealth_by_wrapper_snapshots
    )

    get_data_sources_duration_s = (datetime.now() - start_time).total_seconds()

    if not snapshots_consolidated:
        print("Exiting run:\n empty snapshots")
        return spark, [], 0.0

    spark.sql(f"create database if not exists {db_name};")

    batch_number = 1
    batch_increment = 1000
    overwrite_mode = False
    data_source_n_status = []

    for indx in range(0, len(snapshots_consolidated), batch_increment):
        batch_snapshots = snapshots_consolidated[indx:indx + batch_increment]
        sources = [
            json.dumps({"client_id": snap["client_id"], "snapshot_id": snap["snapshot_id"]}) for snap in batch_snapshots
        ]
        logger_helper = LoggerHelper(source=sources)
        try:
            print(f"Batch {batch_number} - Reading {class_name} data files data to memory...")
            schema_report = snapshot_etl_steps(spark, batch_snapshots, table_class)
            end_indx = indx + batch_increment if indx + batch_increment < len(snapshots_consolidated) else len(snapshots_consolidated)
            print(
                f"Wrote {indx}:{end_indx} data range of {len(snapshots_consolidated)} into {table_class.table_name} with {'overwrite' if overwrite_mode else 'append'} mode\n")

            batch_number += 1
            logger_helper.log_status(schema_report=schema_report)

        except Exception as e:
            logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

        data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, get_data_sources_duration_s


if __name__ == "__main__":
    run_etl(locals())
