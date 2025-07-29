import json
import smart_open
from pyspark.sql import SparkSession, functions as f
from pyspark.sql.dataframe import DataFrame

from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.snake_case_name_change import camel_to_snake_case


def split_files_by_date(file_paths: list) -> dict:
    files_dict = {}
    for path in file_paths:
        path_split = path.split("/")
        date_dict = {"year": path_split[-4], "month": path_split[-3], "day": path_split[-2]}
        file_date = f"{date_dict['year']}-{date_dict['month']}-{date_dict['day']}"
        if file_date in files_dict.keys():
            files_dict[file_date].append(path)
        else:
            files_dict[file_date] = [path]

    return files_dict


def read_json_file(file_path: str) -> dict:
    # Read json data from file
    with smart_open.open(file_path, 'r') as F:
        json_data = json.load(F)
    F.close()
    return json.loads(json_data) if isinstance(json_data, str) else json.loads(json.dumps(json_data))


def append_all_data(spark, spark_df, new_data_collected, table_schema):
    new_data_df = spark.createDataFrame([new_data_collected], table_schema)
    spark_df = spark_df.union(new_data_df)
    return spark_df


def rename_columns_to_snake_case(df):
    # Get the current column names
    old_columns = df.columns
    # Generate new column names in snake_case
    new_columns = [camel_to_snake_case(col_name) for col_name in old_columns]
    # Create a dictionary for renaming
    rename_mapping = {old_columns[i]: new_columns[i] for i in range(len(old_columns))}
    # Rename the columns using select
    df = df.select([f.col(old).alias(new) for old, new in rename_mapping.items()])

    return df


def rename_columns():
    return {'type': 'meeting_type',
            'unparsed_type': 'meeting_type_detail'}


def write_df_to_table(df: DataFrame, col_names: list, table_name: str, overwrite: bool = False):
    df.select(col_names).write.insertInto(table_name, overwrite=overwrite)


def remove_any_rows_existing_in_hive_table(spark, df, table_name):
    ids = [f"'{row.id}'" for row in df.select("id").distinct().collect()]
    spark.sql(f"DELETE FROM {table_name} WHERE id in ({','.join(ids)})")


def create_json_dataframe(spark: SparkSession, file_paths: list) -> DataFrame:
    # Load data into spark dataframe
    return spark.read.json(file_paths)


def add_file_arrival_date(df: DataFrame):
    df = df.withColumn("file_path", f.input_file_name())
    df = df.withColumn("file_arrival_date", f.expr("reverse(split(file_path, '/'))")) \
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


def etl_steps_meetings(spark, file_paths, table_class):
    df = create_json_dataframe(spark, file_paths)
    # Rename columns to snake_case
    df = rename_columns_to_snake_case(df)
    df = add_file_arrival_date(df)

    # Rename columns to more meaningful names
    list_of_cols_to_rename = rename_columns()
    for key, value in list_of_cols_to_rename.items():
        df = df.withColumnRenamed(key, value)
    df, schema_report = reformat_df_data_field_types2(df, table_class)

    # delete any pre-existing rows from table
    remove_any_rows_existing_in_hive_table(spark, df, table_class.table_name)
    # Write to table
    write_df_to_table(df, table_class.get_spark_schema().names, table_class.table_name)

    return schema_report
