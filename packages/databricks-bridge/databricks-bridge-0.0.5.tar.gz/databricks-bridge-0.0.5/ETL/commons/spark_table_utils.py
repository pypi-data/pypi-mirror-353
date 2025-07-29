import os
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import StructType, StructField


essential_field = {"is_essential": True}
non_essential_field = {"is_essential": False}


def non_essentialize_all_other_columns(schema: StructType):
    for i in range(len(schema)):
        if "is_essential" not in schema[i].jsonValue()["metadata"].keys():
            schema[i].metadata = {**schema[i].metadata, **non_essential_field}

    return schema


def create_table_from_schema(table_name, table_schema):
    def _column_metadata(field_schema: StructField):
        metadata_dict = field_schema.jsonValue()['metadata']
        if "mask" in metadata_dict.keys():
            return [f"MASK {metadata_dict['mask_fcn']}"]
        return []

    return f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
    {', '.join(
        [' '.join([field_schema.jsonValue()['name'], field_schema.jsonValue()['type']] + _column_metadata(field_schema))
         for field_schema in table_schema if field_schema.jsonValue()['name'] != ""
         ]
    )}
    )
    {"TBLPROPERTIES (DELTA.enableChangeDataFeed = true)" if os.environ.get('ISDATABRICKS', 'local') == "TRUE" else "USING org.apache.spark.sql.parquet"};
    """

# ALTER TABLE tableName SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
# org.apache.spark.sql.delta.sources.DeltaDataSource


def create_dataframe_with_dict_list(spark: SparkSession, dict_list: list, table_schema: StructType) -> DataFrame:
    # Load data into spark dataframe along with the predefined schema
    return spark.createDataFrame(data=dict_list, schema=table_schema)


def append_to_table_via_schema_evolution(spark: SparkSession, df: DataFrame, table_name):
    alter_existing_table_with_new_df(spark, df, table_name)
    table_describe_collect = spark.sql(f"describe table extended {table_name}").collect()
    table_location = [row.data_type.replace("file:", "").replace("dbfs:", "") for row in table_describe_collect if
                      row.col_name == "Location"][0]
    table_format = "delta" if os.environ.get('ISDATABRICKS', 'local') == "TRUE" else "parquet"
    df.write.format(table_format).option("mergeSchema", "true").mode("append").save(table_location)


def alter_existing_table_with_new_df(spark: SparkSession, new_df: DataFrame, existing_table_name: str):
    existing_table_df = spark.sql(f"select * from {existing_table_name} limit 1")
    logging_table_schema = existing_table_df.schema
    if new_df.schema != logging_table_schema and os.environ.get('ISDATABRICKS', 'local') != "TRUE":
        cols_to_add = [col for col in new_df.columns if col not in existing_table_df.columns]
        cols_to_remove = [col for col in existing_table_df.columns if col not in new_df.columns]
        cols_datatype_to_change = []
        for field_schema in new_df.schema:
            for field_schema2 in existing_table_df.schema:
                if field_schema.name == field_schema2.name and field_schema.dataType != field_schema2.dataType:
                    cols_datatype_to_change.append(field_schema.name)

        if cols_to_add:
            cols_config = [f"{field_schema.name} {field_schema.dataType.typeName()}" for field_schema in new_df.schema if field_schema.name in cols_to_add]
            spark.sql(f"alter table {existing_table_name} add columns ({', '.join(cols_config)});")

        # if cols_to_remove:
        #     spark.sql(f"alter table {existing_table_name} drop columns ({', '.join(cols_to_remove)});")

        # if cols_datatype_to_change:
