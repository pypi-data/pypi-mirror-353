# Databricks notebook source
import shutil
from typing import Tuple
import os
from datetime import datetime
import traceback

from pyspark.sql.dataframe import DataFrame
from pyspark.sql.session import SparkSession
from pyspark.sql.types import StructType
from pyspark.sql.functions import when, expr, lit

from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.spark_table_utils import create_table_from_schema
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.commons.ease_of_use_fcns import delete_checkpoint_dir
from ETL.logging.df_utils.commons import send_table_clients_alert
from ETL.logging.logging_decorators import log_general_info

from ETL.RDS.rds_df_utils.rds_df_utils import RDSConfigTable, db_name, checkpoint_dir

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/rds_integration.py"

rds_config_table_class = RDSConfigTable()
rds_config_table_name = rds_config_table_class.table_name


def get_rds_jdbc_url() -> Tuple[str, dict]:
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        rds_creds_dict = {
            "hostname": os.getenv("RDS_HOST"),
            "port": os.getenv("RDS_PORT"),
            "database": os.getenv("RDS_DATABASE"),
            "username": os.getenv("RDS_USERNAME"),
            "password": os.getenv("RDS_PASSWORD"),
            "driver": os.getenv("RDS_DRIVER"),
        }
    else:
        print("running outside of databricks")
        rds_creds_dict = {"hostname": "", "port": "", "database": "", "username": "", "password": ""}

    url = f"jdbc:postgresql://{rds_creds_dict['hostname']}:{rds_creds_dict['port']}/{rds_creds_dict['database']}"
    return url, rds_creds_dict


def get_rds_table_df(spark: SparkSession, jdbc_url: str, rds_credentials: dict, table_name: str) -> Tuple[DataFrame, float]:
    print(f"Retrieving {table_name} from AWS rds...")
    start_time = datetime.now()
    df = spark.read.format("jdbc") \
        .option("driver", "org.postgresql.Driver") \
        .option("url", jdbc_url) \
        .option("dbtable", f"{table_name}") \
        .option("user", rds_credentials["username"]) \
        .option("password", rds_credentials["password"]) \
        .load()
    duration_s = (datetime.now() - start_time).total_seconds()
    print(f"Retrieved {table_name} from AWS rds after {duration_s} seconds...")
    return df, duration_s


def get_inactive_table_logs(df: DataFrame) -> list:
    inactive_table_and_schema_names_df = df.select(
        expr("concat(table_schema, '.', table_name)")
        .alias("table_and_schema_name")).filter(df.active == False)
    table_and_schema_names = [row.table_and_schema_name for row in inactive_table_and_schema_names_df.collect()]
    return table_and_schema_names


def get_rds_config_df(spark: SparkSession, config_table_name) -> DataFrame:
    spark.sparkContext.setCheckpointDir(checkpoint_dir)
    return spark.sql(f"select * from {config_table_name}").checkpoint()


def delete_checkpoint_dir(env: dict):
    print("Deleting temp checkpoints dir...")
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        env["dbutils"].fs.rm(checkpoint_dir, recurse=True)
    else:
        shutil.rmtree(checkpoint_dir)


def null_sensitive_columns(df: DataFrame, rds_table_dict: dict):
    if "exclude_columns" not in rds_table_dict.keys():
        return df

    print(f'nulling out columns: {rds_table_dict["exclude_columns"]}')
    for _col in rds_table_dict["exclude_columns"]:
        df = df.withColumn(_col, lit(None))

    return df


def insert_rds_table_entry_in_rds_config_table(
        spark: SparkSession, rds_config_df: DataFrame, rds_table_dict: dict, unq_identifier: str, df_schema: StructType
) -> DataFrame:
    table_names_df = rds_config_df.select("table_name", "table_schema")
    table_names = [f"{row.table_schema}.{row.table_name}" for row in table_names_df.collect()]
    rds_table_and_schema_name = rds_table_dict["table_name"]
    if rds_table_and_schema_name not in table_names:
        print(f"Inserting {rds_table_and_schema_name} entry into the {rds_config_table_name} table...")
        rds_schema_name = rds_table_and_schema_name.split(".")[0]
        rds_table_name = rds_table_and_schema_name.split(".")[1]
        uuid = [row.uuid for row in spark.sql("select uuid() as uuid").collect()][0]
        entry_row_df = spark.createDataFrame([
            (uuid,                          # id
             rds_table_name,                # table_name
             rds_schema_name,               # table_schema
             unq_identifier,                # table_unique_identifier
             rds_table_dict["constant"],    # constant
             datetime.now(),                # updated_at
             str(df_schema),                # dataframe_schema
             True)                          # active
        ], rds_config_df.schema)
        rds_config_df_new = rds_config_df.union(entry_row_df)
        return rds_config_df_new

    return rds_config_df


def update_rds_table_entry_in_rds_config_table(
        spark: SparkSession, rds_config_df: DataFrame, rds_table_and_schema_name, df_schema: StructType
) -> Tuple[DataFrame, str]:
    dataframe_schema_collect = rds_config_df.select("id", "dataframe_schema")\
        .filter(expr("concat(table_schema, '.', table_name)") == rds_table_and_schema_name)\
        .collect()
    dataframe_schema_str = [row.dataframe_schema for row in dataframe_schema_collect][0]
    id_str = [row.id for row in dataframe_schema_collect][0]

    if dataframe_schema_str != str(df_schema):
        print(f"Updating {rds_config_table_name} for rds table {rds_table_and_schema_name}...")
        rds_config_df_updated = rds_config_df\
            .withColumn("dataframe_schema",
                        when(rds_config_df.id == id_str, str(df_schema))
                        .otherwise(rds_config_df.dataframe_schema))

        spark.sql(f"drop table if exists {rds_table_and_schema_name}")
        create_databricks_rds_table(spark, rds_table_and_schema_name, df_schema)

        return rds_config_df_updated, id_str

    return rds_config_df, id_str


def create_databricks_rds_table(spark: SparkSession, table_name: str, rds_schema: StructType):
    spark.sql(f"create database if not exists {table_name.split('.')[0]};")
    spark.sql(f"drop table if exists {table_name};")
    try:
        create_table_sql = create_table_from_schema(table_name, rds_schema)
        spark.sql(create_table_sql)
    except Exception as e:
        print(e)
        spark.createDataFrame(data=[], schema=rds_schema).write.saveAsTable(table_name)
        print("Created a df from the schema and saved as table instead")


def overwrite_databricks_rds_table(spark: SparkSession, table_name: str, rds_df: DataFrame):
    print(f"Overwriting databricks {table_name} table...\n")
    create_databricks_rds_table(spark, table_name, rds_df.schema)
    rds_df.write.insertInto(table_name, overwrite=True)


def update_rds_config_table_active_flag(
        spark: SparkSession, rds_config_df: DataFrame, rds_table_dict: dict, id_str: str) -> DataFrame:
    # set active flag to false if initial load table exists in databricks and rds logging table
    current_flag_df = rds_config_df.select("active").filter(rds_config_df.id == id_str)
    current_flag = [row.active for row in current_flag_df.collect()][0]

    if rds_table_dict["constant"] is not bool(current_flag):
        spark.sql(f"select * from {rds_table_dict['table_name']} limit 1")
        rds_config_df = rds_config_df\
            .withColumn("active",
                        when(rds_config_df.id == id_str, rds_table_dict['constant'])
                        .otherwise(rds_config_df.active))

    return rds_config_df


def update_rds_config_table_updated_time(rds_config_df: DataFrame, id_str: str) -> DataFrame:
    rds_config_df_updated = rds_config_df \
        .withColumn("updated_at",
                    when(rds_config_df.id == id_str, expr("CURRENT_TIMESTAMP()"))
                    .otherwise(rds_config_df.updated_at))
    return rds_config_df_updated


def etl_steps(spark: SparkSession, rds_config_df: DataFrame, jdbc_url: str, rds_creds: dict, rds_table_dict: dict, get_data_sources_duration_s: float) -> [DataFrame, float]:
    rds_table_name = rds_table_dict["table_name"]
    rds_table_unq_id = rds_table_dict["unq_id"]
    df, duration_s = get_rds_table_df(spark, jdbc_url, rds_creds, rds_table_name)
    rds_table_schema = df.schema
    df = null_sensitive_columns(df, rds_table_dict)
    rds_config_df = insert_rds_table_entry_in_rds_config_table(spark, rds_config_df, rds_table_dict, rds_table_unq_id, rds_table_schema)
    rds_config_df, id_str = update_rds_table_entry_in_rds_config_table(spark, rds_config_df, rds_table_name, rds_table_schema)
    overwrite_databricks_rds_table(spark, rds_table_name, df)
    rds_config_df = update_rds_config_table_active_flag(spark, rds_config_df, rds_table_dict, id_str)
    rds_config_df = update_rds_config_table_updated_time(rds_config_df, id_str)

    return rds_config_df, get_data_sources_duration_s + duration_s


@log_general_info(
    env=locals(),
    etl_data="rds_integration",
    script_path=script_path,
    data_sources_type="rds"
)
def run_etl(env: dict):
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    sc.setLogLevel("ERROR")
    spark.sql(f"create database if not exists {db_name};")

    jdbc_url, rds_creds_dict = get_rds_jdbc_url()
    spark.sql(rds_config_table_class.create_table())
    rds_config_df = get_rds_config_df(spark, rds_config_table_name)
    tables_dict = rds_config_table_class.get_rds_tables_dict()
    inactive_table_names = get_inactive_table_logs(rds_config_df)

    data_source_n_status = []
    get_data_sources_duration_s = 0.0

    for table_dict in tables_dict:
        if table_dict["table_name"] not in inactive_table_names or (table_dict["table_name"] in inactive_table_names and table_dict["constant"]):
            logger_helper = LoggerHelper(source=table_dict["table_name"])
            print(table_dict["table_name"])
            try:
                rds_config_df, get_data_sources_duration_s = etl_steps(spark, rds_config_df, jdbc_url, rds_creds_dict, table_dict, get_data_sources_duration_s)
                logger_helper.log_status()
            except Exception as e:
                send_table_clients_alert(env=env, spark=spark, table_name=table_dict["table_name"])
                logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

            data_source_n_status.append(logger_helper.source_n_status)

    # rds_config_df.show()
    rds_config_df.write.insertInto(rds_config_table_name, overwrite=True)
    delete_checkpoint_dir(env)

    return spark, data_source_n_status, get_data_sources_duration_s


if __name__ == "__main__":
    run_etl(locals())

# export PYTHONPATH="${PYTHONPATH}:/full/path/to/the/lakehouse"
# spark-submit --jars ETL/commons/jar_files/postgresql-9.1-901-1.jdbc4.jar ETL/RDS/rds_integration.py
