from decimal import Decimal
from datetime import datetime
from smart_open import smart_open
import humps
import json
import copy
import os
import subprocess
from pyspark.sql.dataframe import DataFrame
from pyspark.sql import functions as f
from pyspark.sql.functions import col, when, lit, to_date, to_timestamp, trim, to_json
from pyspark.sql.types import StructType, StringType, IntegerType, LongType, DoubleType, BooleanType
from ETL.commons.normalize_data import get_nested_df_paths
from ETL.commons.ease_of_use_fcns import SchemaReport


def reformat_dict_data_field_types(dict_data: dict, table_schema: StructType) -> dict:
    """
    :param dict_data:
    :param table_schema:
    :return: dict_data
    """
    # reformat data for predefined schema
    list_dict_keys = [key for key in dict_data.keys() if isinstance(dict_data[key], (list, dict))]
    table_schema_roi = [field_schema for field_schema in table_schema if field_schema.name in list_dict_keys or field_schema.jsonValue()["type"] != "string"]
    for field_schema in table_schema_roi:
        field_schema_dict = field_schema.jsonValue()
        field_name = field_schema_dict["name"]
        field_dtype = field_schema_dict["type"]

        if isinstance(dict_data[field_name], (int, float, str)) and "decimal" in field_dtype:
            dict_data[field_name] = Decimal(str(dict_data[field_name]))
        elif isinstance(dict_data[field_name], str) and field_dtype in ["long", "integer"]:
            dict_data[field_name] = int(str(dict_data[field_name]))
        elif isinstance(dict_data[field_name], (int, str)) and field_dtype in ["float", "double"]:
            dict_data[field_name] = float(str(dict_data[field_name]))
        elif isinstance(dict_data[field_name], str) and field_dtype in ["boolean"]:
            dict_data[field_name] = eval(dict_data[field_name].capitalize())
        elif isinstance(dict_data[field_name], str) and field_dtype == "timestamp":
            timestamp_str = dict_data[field_name][:-2] if "Z" in dict_data[field_name][-1] else dict_data[field_name]
            datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
            # add microseconds to seconds if it doesn't
            timestamp_str_new = timestamp_str+".0" if "." not in timestamp_str else timestamp_str
            dict_data[field_name] = datetime.strptime(timestamp_str_new[:23], datetime_format)
        elif isinstance(dict_data[field_name], str) and field_dtype == "date":
            date_str = dict_data[field_name]
            date_format = "%Y-%m-%d"
            dict_data[field_name] = datetime.strptime(date_str, date_format)
        elif isinstance(dict_data[field_name], (dict, list)) and field_dtype == "string":
            json_dict = {field_name: convert_nested_dict_to_nested_list_of_dict(dict_data[field_name])}
            dict_data[field_name] = json.dumps(json_dict)

    return dict_data


def get_missing_essential_fields(df: DataFrame, table_class):
    missing_fields = []
    for _col in table_class.get_spark_schema():
        if _col.name not in df.columns:
            if "is_essential" in _col.jsonValue()["metadata"].keys():
                missing_fields += [_col.name] if _col.jsonValue()["metadata"]["is_essential"] else []
            else:
                missing_fields.append(_col.name)

    # missing_fields = [_col for _col in table_class.get_spark_schema() if _col.name not in df.columns and (_col.jsonValue()["metadata"]) ]
    return missing_fields


def reformat_df_data_field_types(df: DataFrame, table_class):
    missing_fields = get_missing_essential_fields(df, table_class)
    # Collect table schema field names and types
    schema_col_names_and_types = {}
    for field_schema in table_class.get_spark_schema():
        schema_col_names_and_types[field_schema.jsonValue()["name"]] = field_schema.jsonValue()["type"]

    date_formats = table_class.date_format
    # build cast data types pyspark df.select command
    format_str_list = []
    fields_in_raw_df_but_not_in_schema = []
    for col_name in df.columns:
        if col_name in schema_col_names_and_types:
            col_format_str = f'trim("{col_name}").alias("{col_name}")'
            field_type = schema_col_names_and_types[col_name]

            if field_type == "date":
                date_format = date_formats["*"] if "*" in date_formats else date_formats[col_name]
                col_format_str = f"to_date(trim(col('{col_name}')), '{date_format}').alias('{col_name}')"

            elif field_type == "timestamp":
                date_format = date_formats["*"] if "*" in date_formats else date_formats[col_name]
                if "T" in date_format:
                    col_format_str = f"to_timestamp(trim('{col_name}')).alias('{col_name}')"
                else:
                    col_format_str = f"to_timestamp(trim('{col_name}'), '{date_format}').alias('{col_name}')"

            elif field_type == "double":
                col_format_str = f"trim(col('{col_name}')).cast(DoubleType()).alias('{col_name}')"

            elif field_type in "integer":
                col_format_str = f"trim(col('{col_name}')).cast(IntegerType()).alias('{col_name}')"

            elif field_type in "long":
                col_format_str = f"trim(col('{col_name}')).cast(LongType()).alias('{col_name}')"

            elif field_type == "boolean":
                col_format_str = f"trim(col('{col_name}')).cast(BooleanType()).alias('{col_name}')"

            format_str_list.append(col_format_str)
        else:
            unq_missing_field_val = df.select(col_name).distinct().collect()
            missing_field = {
                "field": col_name,
                "unq_val": [row[col_name] for row in unq_missing_field_val if row[col_name] is not None]
            }
            fields_in_raw_df_but_not_in_schema.append(missing_field)

    df_format_str = "df.select(" + ",".join(format_str_list) + ")"
    df_formatted = eval(df_format_str)
    df_complete = add_missing_fields_from_schema(df_formatted, table_class.get_spark_schema())
    df_reformatted = null_all_empty_df_cells(df_complete)
    schema_report = SchemaReport(
        unexpected_fields=fields_in_raw_df_but_not_in_schema,
        missing_expected_fields=missing_fields,
        class_name=table_class.__class__.__name__,
        data_lineage=table_class.data_lineage if hasattr(table_class, 'data_lineage') else None
    )
    return df_reformatted, schema_report


def reformat_df_data_field_types2(df: DataFrame, table_class):
    missing_fields = get_missing_essential_fields(df, table_class)
    # Collect table schema field names and types
    schema_col_names_and_types = {}
    for field_schema in table_class.get_spark_schema():
        schema_col_names_and_types[field_schema.jsonValue()["name"]] = field_schema.jsonValue()["type"]

    try:
        date_formats = table_class.date_format
    except Exception as e:
        date_formats = {}

    fields_in_raw_df_but_not_in_schema = []
    for col_name in df.columns:
        if col_name in schema_col_names_and_types:
            field_type = schema_col_names_and_types[col_name]

            if field_type == "date" and field_type != df.select(col_name).schema[0].dataType.typeName():
                if date_formats:
                    date_format = date_formats["*"] if "*" in date_formats else date_formats[col_name]
                    # col_format_str = f"to_date(trim(col('{col_name}')), '{date_format}').alias('{col_name}')"
                    df = df.withColumn(col_name, to_date(trim(df[col_name]).cast(StringType()), date_format))
                else:
                    df = df.withColumn(col_name, to_date(trim(df[col_name]).cast(StringType())))

            elif field_type == "timestamp" and field_type != df.select(col_name).schema[0].dataType.typeName():
                if date_formats:
                    date_format = date_formats["*"] if "*" in date_formats else date_formats[col_name]
                    if "T" in date_format:
                        # col_format_str = f"to_timestamp(trim('{col_name}')).alias('{col_name}')"
                        df = df.withColumn(col_name, to_timestamp(trim(df[col_name]).cast(StringType())))
                    else:
                        # col_format_str = f"to_timestamp(trim('{col_name}'), '{date_format}').alias('{col_name}')"
                        df = df.withColumn(col_name, to_timestamp(trim(df[col_name]).cast(StringType()), date_format))
                else:
                    df = df.withColumn(col_name, to_timestamp(trim(df[col_name].cast(StringType()))))

            elif field_type == "string" and df.select(col_name).schema[0].dataType.typeName() in ["array", "struct"]:
                df = df.withColumn(col_name, to_json(col(col_name)))

            elif field_type != df.select(col_name).schema[0].dataType.typeName():
                df = df.withColumn(col_name, trim(df[col_name].cast(StringType())).cast(field_type))

        else:
            unq_missing_field_val = df.select(col_name).distinct().limit(10).collect()
            missing_field = {
                "field": col_name,
                "unq_val": [row[col_name] for row in unq_missing_field_val if row[col_name] is not None]
            }
            fields_in_raw_df_but_not_in_schema.append(missing_field)

    df_complete = add_missing_fields_from_schema(df, table_class.get_spark_schema())
    # df_reformatted = null_all_empty_df_cells(df_complete)
    schema_report = SchemaReport(
        unexpected_fields=fields_in_raw_df_but_not_in_schema,
        missing_expected_fields=missing_fields,
        class_name=table_class.__class__.__name__,
        data_lineage=table_class.data_lineage if hasattr(table_class, 'data_lineage') else None
    )
    return df_complete, schema_report


def df_targeted_explosion(df: DataFrame, explodables: dict) -> DataFrame:
    all_query_paths, _ = get_nested_df_paths(df)
    select_str = []
    for col_name in df.columns:
        if col_name in explodables:
            select_str += [
                f"{col_name}.{child} as {col_name}_{humps.decamelize(child.replace('.', ''))}"
                for child in explodables[col_name]
                if f"{col_name}.{child}" in all_query_paths
            ]
        else:
            select_str.append(col_name)

    return df.selectExpr(select_str)


def add_missing_fields_from_schema(df: DataFrame, table_schema) -> DataFrame:
    missing_fields_from_df = {}
    for field_schema in table_schema:
        col_name = field_schema.jsonValue()["name"]
        if col_name not in df.columns:
            missing_fields_from_df[col_name] = field_schema.jsonValue()["type"]

    if missing_fields_from_df:
        df_format_str = ', '.join([f'lit(None).cast("{dtype}").alias("{field_name}")' for field_name, dtype in missing_fields_from_df.items()])
        df_new = eval(f"df.select('*', {df_format_str})")
        return df_new

    return df


def none_empty_dict_fields(dict_data: dict) -> dict:
    for key, val in dict_data.items():
        if val == "":
            dict_data[key] = None
    return dict_data


def null_all_empty_df_cells(df: DataFrame) -> DataFrame:
    return df.select([when(col(c) == "", None).otherwise(col(c)).alias(c) for c in df.columns])


def check_for_dict_data_expected_fields(dict_data: dict, table_schema: StructType) -> dict:
    # Check for all expected fields
    dict_field_names = dict_data.keys()
    schema_field_names = [field_schema.jsonValue()["name"] for field_schema in table_schema]
    missing_keys = list(set(schema_field_names) - set(dict_field_names))
    for m_key in missing_keys:
        dict_data[m_key] = None

    return dict_data


def add_file_arrival_date(dict_data: dict, file_arrival_date: str) -> dict:
    date_format = '%Y-%m-%d'
    date_time = datetime.strptime(file_arrival_date, date_format)
    dict_data["file_arrival_date"] = date_time.date()

    return dict_data


def add_file_path_df(df: DataFrame, file_path_col: str = "file_path"):
    return df.withColumn(file_path_col, f.input_file_name())


def add_file_arrival_date_df(df: DataFrame, file_path_col: str = "file_path", drop_path_col: bool = False) -> DataFrame:
    df = df.withColumn("file_path_split", f.split(f.col(file_path_col), "/")) \
        .withColumn("_day", f.col("file_path_split").getItem(f.size(f.col("file_path_split")) - 2)) \
        .withColumn("_month", f.col("file_path_split").getItem(f.size(f.col("file_path_split")) - 3)) \
        .withColumn("_year", f.col("file_path_split").getItem(f.size(f.col("file_path_split")) - 4)) \
        .withColumn("file_arrival_date", f.concat_ws("-", f.col("_year"), f.col("_month"), f.col("_day"))) \
        .drop(*["_year", "_month", "_day", "file_path_split"])
    if drop_path_col:
        df = df.drop(file_path_col)
    return df


def drop_file_path_col_df(df: DataFrame, file_path_col: str = "file_path") -> DataFrame:
    return df.drop(file_path_col)


def add_file_path(dict_data: dict, file_path: str) -> dict:
    dict_data["file_path"] = file_path
    return dict_data


def add_file_id(dict_data: dict, file_id: str) -> dict:
    dict_data["file_id"] = file_id
    return dict_data


def uningested_fields(dict_list: list, table_schema: StructType) -> list:
    data_fields = [list(el.keys()) for el in dict_list]
    data_fields_unq = list(set(sum(data_fields, [])))
    schema_fields = [field_schema.jsonValue()["name"] for field_schema in table_schema]
    missing_fields = [field for field in data_fields_unq if field not in schema_fields]
    return missing_fields


def clean_dict_field_names(dict_data: dict, rm_prefix: str) -> dict:
    new_dict_data = {}
    for key, value in dict_data.items():
        new_key = key.replace(" ", "").replace("-", "").replace("@", "")
        new_key = new_key.replace(rm_prefix, "") if new_key[:len(rm_prefix)] == rm_prefix else new_key
        new_dict_data[new_key] = value

    return new_dict_data


def camel_to_snake_case(dict_data: dict) -> dict:
    # Rename fields from camel case to snake case
    new_dict_data = {}
    for key, val in dict_data.items():
        new_key = humps.decamelize(key)
        new_dict_data[new_key] = val

    return new_dict_data


def camel_to_snake_case_df(df: DataFrame) -> DataFrame:
    for col_name in df.columns:
        df = df.withColumnRenamed(col_name, humps.decamelize(col_name))

    return df


def rename_df_cols(df: DataFrame) -> DataFrame:
    col_renamed = [f"{col_name} as {humps.decamelize(col_name).replace('__', '_')}" for col_name in df.columns]
    df = df.selectExpr(col_renamed)
    return df


def convert_nested_dict_to_nested_list_of_dict(data: [list, dict]) -> list:

    def recur(data: [list, dict], in_list: bool):

        if isinstance(data, list):
            for indx, el in enumerate(data):
                data[indx] = copy.copy(recur(el, True))
        elif isinstance(data, dict) and in_list:
            temp_data = copy.copy(data)
            for key, val in data.items():
                temp_data[key] = copy.copy(recur(val, False))
            data = temp_data
        elif isinstance(data, dict) and not in_list:
            data = copy.copy(recur([data], False))
        else:
            pass

        return data

    return recur(data, False)


def extract_file_date_from_df(df: DataFrame):
    df = df.withColumn("file_path", f.input_file_name())
    df = df.withColumn("file_arrival_date", f.expr("reverse(split(file_path, '/'))"))\
        .withColumn(
            "file_arrival_date",
            f.concat_ws(
                "-",
                f.array(
                    f.col("file_arrival_date").getItem(3),
                    f.col("file_arrival_date").getItem(2),
                    f.col("file_arrival_date").getItem(1)
                )
            )
    )
    return df.drop("file_path")
