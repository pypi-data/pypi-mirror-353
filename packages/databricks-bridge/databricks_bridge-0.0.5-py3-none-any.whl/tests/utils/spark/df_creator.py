from typing import Dict, List, Any, Union
import json

from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import StructType, Row

from tests.exceptions import TestingException


def create_spark_dataframe(
        spark: SparkSession,
        column_names: List,
        *rows: List[Any],
        schema: StructType = None
) -> DataFrame:
    data_rows = [tuple(row) for row in rows]
    try:
        dataframe = spark.createDataFrame(data=data_rows, schema=schema).toDF(*column_names)
    except ValueError as e:
        raise ValueError(f"Make sure your row data is all equal length. Error: {e}")
    except Exception as e:
        raise TestingException(f"Something has gone wrong: {e}")

    return dataframe


def dict_data_spark_dataframe_creator(
        spark: SparkSession,
        data: Union[Dict, List[Dict]],
        schema: StructType = None,
        infer_schema: bool = False
) -> DataFrame:
    if isinstance(data, (dict, list)) and infer_schema:
        return spark.read.json(spark.sparkContext.parallelize([json.dumps(data)]))
    elif isinstance(data, dict):
        return spark.createDataFrame([data], schema=schema)
    elif isinstance(data, list):
        return spark.createDataFrame(data, schema=schema)
    else:
        raise TypeError("Wrong data type, must be dict or list")


def json_files_spark_dataframe_creator(
        spark: SparkSession,
        file: Union[str, List]
) -> DataFrame:
    try:
        return spark.read.json(file)
    except Exception as e:
        print(e)
        raise TypeError("Wrong data type, must be string path or list of string paths")


def csv_file_spark_dataframe_creator(
        spark: SparkSession,
        file_path: str,
        schema: StructType = None
) -> DataFrame:
    try:
        if schema:
            return spark.read.format("csv").option("header", True).option("multiline", True).schema(schema).load(file_path)
        else:
            return spark.read.format("csv").option("header", True).option("multiline", True).option("escape", "\"").load(file_path)
    except Exception as e:
        raise TypeError("Wrong data type, must be dict or list")


def csv_list_spark_dataframe_creator(
        spark: SparkSession,
        csv_data: list,
        delimiter: str,
        inferSchema: bool,
        schema: StructType = None
) -> DataFrame:
    csv_rdd = spark.sparkContext.parallelize(csv_data)
    try:
        if not schema:
            return spark.read.option("header", True).option("delimiter", delimiter).option("inferSchema", inferSchema).csv(csv_rdd)
        else:
            return spark.read.option("header", True).option("delimiter", delimiter).schema(schema).csv(csv_rdd)
    except Exception as e:
        raise TypeError("Wrong data type, must be list")


def row_data_spark_dataframe_creator(
        spark: SparkSession,
        row_list: Row
) -> DataFrame:
    try:
        return spark.createDataFrame(row_list)
    except Exception as e:
        print(e)
