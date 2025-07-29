# Databricks notebook source
from typing import Tuple
import os
import traceback
import time

from pyspark.sql import SparkSession
from ETL.bc_hv_pt_historicals.df_utils.historicals_df_utils import get_table_listings
from ETL.bc_hv_pt_historicals.df_utils.common_fcns import (
    get_target_columns, etl_steps, delete_checkpoint_dir, prep_bc_pt_table, prep_hv_table
)

from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info


set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/bc_hv_pt_historicals_etl.py"


@log_general_info(
    env=locals(),
    etl_data="bc_hv_pt_historicals",
    script_path=script_path,
    data_sources_type="lakehouse"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    data_source_n_status = []

    for table_dict in get_table_listings():
        src_table_name = table_dict["table_name"]
        logger_helper = LoggerHelper(source=src_table_name)
        print(f"Source table: {src_table_name}...")

        try:
            target_columns = get_target_columns(table_dict)
            target_columns_str = ", ".join(target_columns)
            df_init = spark.sql(f"select {target_columns_str} from {src_table_name}")
            src_table_schema = df_init.schema

            group_id_list = [
                row.group_id for row in spark.sql(
                    f"select distinct {table_dict['cols']['group_id_col']} as group_id from {src_table_name};"
                ).collect()
            ]

            for hist_version in ["bc", "hv", "pt"]:

                if hist_version in ["bc", "pt"]:
                    table_class = prep_bc_pt_table(spark, src_table_schema, hist_version, table_dict)
                elif hist_version == "hv":
                    table_class = prep_hv_table(spark, df_init, hist_version, table_dict)

                batch_increment = 50000
                batch_num = 1
                print("Commencing batch processing")
                for indx in range(0, len(group_id_list), batch_increment):
                    batch_ids = group_id_list[indx:indx + batch_increment]
                    try:
                        etl_steps(spark, df_init, table_dict, hist_version, table_class, batch_ids)
                        end_indx = indx + batch_increment if indx + batch_increment < len(group_id_list) else len(group_id_list)
                        print(f"Batch {batch_num} | Processed {indx}:{end_indx} data range of {len(group_id_list)}")
                        batch_num += 1

                        logger_helper.log_status()

                    except Exception as e:
                        msg = f"Error on {src_table_name} {hist_version} creation:\n{traceback.format_exc()}"
                        logger_helper.log_status(traceback=msg, failed=True)

                    data_source_n_status.append(logger_helper.source_n_status)

                print(f"Updated {hist_version} table for the source table: {src_table_name}\n")

        except Exception as e:
            msg = f"Error on reading from {src_table_name}:\n{traceback.format_exc()}"
            logger_helper.log_status(traceback=msg, failed=True)

            data_source_n_status.append(logger_helper.source_n_status)

    delete_checkpoint_dir(env)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())
