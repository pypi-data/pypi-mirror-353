# Databricks notebook source
from pyspark.sql.functions import arrays_zip, explode, split
from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import StructType
import copy
import os
from typing import Tuple
import json
from datetime import datetime, timedelta
import traceback
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.normalize_data import explode_df_level_by_array_level
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.logging.logging_decorators import log_general_info
from ETL.commons.spark_table_utils import create_table_from_schema
from ETL.commons.reformat_data import camel_to_snake_case_df

from ETL.scripts.asset.df_utils.morningstar_IFLS_reg_exp_df_utils import ColumnClasses, MorningstarXMLTable, db_name

script_path = f"{os.path.abspath('')}/morningstar_IFLS_reg_exp.py"


def get_nested_df_paths(df, nested_children=[]):
    '''
    Function already exists in ETL.commons.normalize_data but was included in this script to eliminate the 'No such struct fields xmlns' error as a temp fix
    '''
    def recur(df_json_schema, cur_col_name, query_paths):
        df_field_schemas = df_json_schema["fields"]
        next_nest_cols = []
        failed_cols = []
        for field_schema in df_field_schemas:
            field_name = field_schema["name"]
            field_name = cur_col_name if field_name in cur_col_name else field_name
            field_type = field_schema["type"]
            if isinstance(field_type, dict):
                field_type_type = field_type["type"]

                if field_type_type == "array" and isinstance(field_type["elementType"], dict):
                    field_type_element_type = field_type["elementType"]
                    needs_index = True if field_type_element_type["type"] == "array" else False
                    if needs_index:
                        array_fields = field_type_element_type["elementType"]["fields"]
                        next_nest_cols = [f"{field_name}[0].{nested_field['name']}" for nested_field in array_fields]
                    else:
                        struct_fields = field_type_element_type["fields"]
                        next_nest_cols = [f"{field_name}.{nested_field['name']}" for nested_field in struct_fields]

                elif field_type_type == "struct":
                    struct_fields = field_type["fields"]
                    next_nest_cols = [f"{field_name}.{nested_field['name']}" for nested_field in struct_fields]

                query_paths += next_nest_cols 

                for col in next_nest_cols:
                    '''
                    If statement included to remove error 'No such struct field xmlns'
                    '''
                    if col != 'fund_share_class__fund__portfolio_list.fund_share_class__fund__portfolio_list.SurveyData[0].xmlns:xsi':
                        query_paths = copy.copy(recur(df.selectExpr(col).schema.jsonValue(), col, query_paths))

        return query_paths

    all_query_paths = recur(df.schema.jsonValue(), "", [])
    nested_children_paths = [query_path for query_path in all_query_paths for child in nested_children if
                            child in query_path]

    return all_query_paths, nested_children_paths


def clean_data(spark: SparkSession, sc: SparkContext, nested_col_name: str, field_name: list) -> Tuple[DataFrame, float]:
    query = f"""
            select {nested_col_name}
                    , fund_share_class__id AS msid
                    , LEFT(RIGHT(file_path, INSTR(REVERSE(file_path),'/')-1), INSTR(RIGHT(file_path, INSTR(REVERSE(file_path), '/')-1), '.') - 1) AS isin 
            from loaded.asset_morningstar_xml_isin_dataoutput where {nested_col_name} is not null
            """
    start_time = datetime.now()
    df = spark.sql(query)
    query_duration_sec = (datetime.now() - start_time).total_seconds()
    data = df.collect()
    data_list = []
    unq_id = 'isin'

    for row in data:
        json_data = json.loads(row[nested_col_name])
        json_data = {nested_col_name: json_data}
        json_data[unq_id] = row[unq_id]
        json_data['msid'] = row['msid']
        data_list.append(json_data)
    df = spark.read.json(sc.parallelize([json.dumps(data_list)]))
    target_keys = [path.split(".")[-1] for path in field_name]
    all_paths, expected_query_paths = get_nested_df_paths(df, target_keys)
    final_df = df.select(unq_id, 'msid')

    for i in field_name:
        target_path = [path for path in expected_query_paths if f"""{nested_col_name}.{nested_col_name}.{i}""" == path.replace("[0]", "")][0]
        df2 = explode_df_level_by_array_level(df, unq_id, target_path)
        final_df = final_df.join(df2, final_df.isin == df2.isin, "left").drop(df2.isin).dropDuplicates()
        final_df = final_df.withColumnRenamed(final_df.columns[2], 'BreakdownValue')
        final_df = final_df.select(final_df.isin, final_df.msid, explode(final_df.BreakdownValue).alias('exploded_BreakdownValue'))
        final_df = final_df.select(final_df.isin, final_df.msid, final_df.exploded_BreakdownValue.type.alias('breakdown_type'), final_df.exploded_BreakdownValue.value.alias('breakdown_value'))

    return final_df, query_duration_sec


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str, overwrite_mode: bool):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite_mode)


def etl_steps(spark: SparkSession, sc: SparkContext, column_classes: list, data_sources_duration_s: float) -> float:

    for column_class in column_classes:
        df, query_duration_sec = clean_data(spark, sc,  column_class.field_name, column_class.target_field_path)
        data_sources_duration_s += query_duration_sec
        if column_class != column_classes[0]:
            final_df = final_df.join(df, final_df.isin == df.isin, "full").drop(df.isin).dropDuplicates()
        else:
            final_df = df

    table_class = MorningstarXMLTable()
    table_schema = table_class.get_spark_schema()
    spark.sql(table_class.create_table())
    write_files_to_tables(final_df, table_schema.names, table_class.table_name, True)
    return data_sources_duration_s


@log_general_info(
    env=locals(),
    etl_data="morningstar_IFLS_reg_exp",
    script_path=script_path,
    data_sources_type="lakehouse"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)

    spark.sql(f"create database if not exists {db_name};")

    data_sources_duration_s = 0.0
    base_table_name = 'loaded.asset_morningstar_xml_isin_dataoutput'
    parquet_files_dir = "/Users/arsaselvaratnam/Documents/manual_export_parquet/asset_morningstar_xml_isin_dataoutput_251122/*"

    if os.environ.get('ISDATABRICKS', 'local') != "TRUE":
        df = spark.read.parquet(parquet_files_dir)
        spark.sql(f"create database if not exists {base_table_name.split('.')[0]};")
        spark.sql(create_table_from_schema(base_table_name, df.schema()))
        df.write.insertInto(base_table_name, overwrite=True)
    
    column_classes = ColumnClasses().instantiate
    logger_helper = LoggerHelper(source=base_table_name)
    data_source_n_status = []

    try:
        data_sources_duration_s = etl_steps(spark, sc, column_classes, data_sources_duration_s)
        logger_helper.log_status()
    except:
        logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

    data_source_n_status.append(logger_helper.source_n_status)
    
    return spark, data_source_n_status, data_sources_duration_s


if __name__ == "__main__":
    run_etl(locals())