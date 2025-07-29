# Databricks notebook source
from pyspark.sql.functions import explode_outer, expr
from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import StructType
import os
from typing import Tuple
from datetime import datetime
import traceback
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.logging.logging_decorators import log_general_info
from ETL.commons.spark_table_utils import create_table_from_schema
from ETL.commons.reformat_data import camel_to_snake_case_df
from ETL.commons.json_query_handler import JsonQueryHandler

from ETL.scripts.asset.df_utils.morningstar_IFLS_market_capital_breakdown_df_utils import ColumnClasses, MorningstarXMLTable, db_name

script_path = f"{os.path.abspath('')}/morningstar_IFLS_market_capital_breakdown.py"
    

def explode_array_and_map_columns(df):
    '''
    function explodes all the columns that are of type array or map

    arg:
    df -> Dataframe

    output:
    exploded_df -> Dataframe
    '''
    array_cols = [col for col, dtype in df.dtypes if dtype.startswith("array")]
    map_cols = [col for col, dtype in df.dtypes if dtype.startswith("map")]

    exploded_df = df
    for col in array_cols:
        exploded_df = exploded_df.withColumn(col, explode_outer(col))

    for col in map_cols:
        exploded_df = exploded_df.withColumn(col, explode_outer(explode_outer(expr(f"map_entries({col})")))) \
            .withColumn(f"{col}_key", col(col)["key"]) \
            .withColumn(f"{col}_value", col(col)["value"]) \
            .drop(col)

    return exploded_df


def clean_data(spark: SparkSession, sc: SparkContext, nested_col_name: str, field_name: list) -> Tuple[DataFrame, float]:
    '''
    function performs all normalisation and transformations needed on this dataset

    arg:
    spark -> SparkSession
    sc -> SparkContext
    nested_col_name -> str containing the name of the nested column as specified from the original table
    field_name -> str containing paths needed to extract the required data

    output:
    final_df -> Dataframe
    query_duration_sec -> float
    '''
    jsonQueryHandler = JsonQueryHandler()
    query = f"""
            SELECT {nested_col_name}
                    , fund_share_class__id as msid
                    , SUBSTRING_INDEX(SUBSTRING_INDEX(file_path, '/', -1), '.', 1) AS isin 
            FROM loaded.asset_morningstar_xml_isin_dataoutput 
            WHERE {nested_col_name} IS NOT NULL
            """
    unq_id = ['isin', 'msid']
    start_time = datetime.now()
    df = jsonQueryHandler.get_nested_json_table_df(spark, query)
    query_duration_sec = (datetime.now() - start_time).total_seconds()

    list_of_cols = unq_id
    for i in field_name:
        list_of_cols.append(f"""{nested_col_name}.{nested_col_name}.{i}""")
    final_df = df.select(list_of_cols)

    for i in range(5):
        final_df = explode_array_and_map_columns(final_df)

    unq_id = ['isin', 'msid']
    new_list_of_cols = []
    for i in final_df.columns:
        if i not in unq_id:
            i = i + '.*'
            new_list_of_cols.append(i)
        else:
            new_list_of_cols.append(i)
    final_df = final_df.select(*new_list_of_cols)

    for i in final_df.columns:
        if i == 'Type':
            final_df = final_df.withColumnRenamed(i, 'breakdown_'+i)
        elif i == 'Value':
           final_df = final_df.withColumnRenamed(i, 'breakdown_'+i)

    final_df = final_df.na.drop('any')   

    return final_df, query_duration_sec

def rename_df(df: DataFrame, schema: StructType) -> DataFrame:
    '''
    function renames the columns to lakehouse standard column names (i.e. using _ and all lower case)

    arg:
    df -> Dataframe containing the data that needs to be renamed
    schema -> StructType containing the structure of the destination table 

    output:
    df_snake_case -> Dataframe 
    '''

    df_snake_case = camel_to_snake_case_df(df)
    for col_name in df_snake_case.columns:
        df_snake_case = df_snake_case.withColumnRenamed(col_name, col_name.replace('__','_'))

    df_snake_case_cols = df_snake_case.columns

    col_names = schema.names
    for col_name in col_names:
        col_name_matches = [col for col in df_snake_case_cols if col_name in col.lower()]
        col_name_match = col_name_matches[0] if len(col_name_matches) < 2 else min(set(col_name_matches), key=len)
        df_snake_case = df_snake_case.withColumnRenamed(col_name_match, col_name)

    return df_snake_case


def write_files_to_tables(df: DataFrame, col_names: list, table_name: str, overwrite_mode: bool):
    '''
    function that writes to the destination table

    arg:
    df -> Dataframe
    col_names -> list
    table_name -> str containing the name of the table as specified from the df_utils
    overwrite_mode -> bool where true overwrites the table and false appends to it
    '''
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite_mode)


def etl_steps(spark: SparkSession, sc: SparkContext, column_classes: list, data_sources_duration_s: float) -> float:
    '''
    function performs all normalisation and transformations needed on this dataset

    arg:
    spark -> SparkSession
    sc -> SparkContext
    column_classes -> list containing table and column structures outlined in df_utils
    data_sources_duration_s -> float containing number of seconds it took to run the queries in this script

    output:
    query_duration_sec -> float
    '''

    for column_class in column_classes:
        df, query_duration_sec = clean_data(spark, sc,  column_class.field_name, column_class.target_field_path)
        data_sources_duration_s += query_duration_sec
        if column_class != column_classes[0]:
            final_df = final_df.join(df, final_df['isin'] == df['isin'], "full").drop(df.isin).dropDuplicates()
        else:
            final_df = df

    table_class = MorningstarXMLTable()
    table_schema = table_class.get_spark_schema()
    spark.sql(table_class.create_table())
    renamed_df = rename_df(final_df, table_schema)
    write_files_to_tables(renamed_df, table_schema.names, table_class.table_name, True)

    return data_sources_duration_s


@log_general_info(
    env=locals(),
    etl_data="morningstar_IFLS_market_capital_breakdown",
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