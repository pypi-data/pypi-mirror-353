import humps
import smart_open
from pyspark.sql import SparkSession, functions as f
from pyspark.sql.dataframe import DataFrame

from ETL.commons.reformat_data import reformat_df_data_field_types2
from ETL.commons.unittest_utils import create_tempfile_from_string_data


def read_csv_file(file_path: str) -> list:
    file = smart_open.open(file_path, 'rb', encoding="utf8")  # .decode('utf-8')
    csv_data = file.read()
    file.close()
    return csv_data


def create_csv_dataframe(spark: SparkSession, file_content: str) -> DataFrame:
    # Load data into spark dataframe along with the predefined schema
    temp_file_path = create_tempfile_from_string_data(file_content.encode())
    return spark.read.option("header", True).option("multiline", True).csv(temp_file_path)


def create_dataframe(spark: SparkSession, file_path: str) -> DataFrame:
    # Load data into spark dataframe along with the predefined schema
    return spark.read.parquet(file_path)


def get_filename_attr(file_path: str) -> str:
    file_tag = file_path.split("/")[-1].replace("_all.parquet", "").replace("_all.csv", "").replace(".csv", "").lower()
    file_tag = "email_message" if file_tag == "emailmessage" else file_tag
    file_tag = "tn_cs" if file_tag == "t_c" else file_tag
    class_name = humps.pascalize(file_tag) + "Table"

    return class_name


def table_equals_defined_schema(spark: SparkSession, table_name, table_class):
    remote_schema = spark.sql(f"select * from {table_name} limit 1;").schema
    defined_schema = table_class.get_spark_schema()
    json_schema_fcn = lambda _schema: [{"name": el["name"], "type": el["type"]} for el in _schema.jsonValue()["fields"]]
    return json_schema_fcn(remote_schema) == json_schema_fcn(defined_schema)


def etl_steps(spark: SparkSession, table_class, file_path: str, overwrite: bool = True, file_content: str = "", catalog_name: str = ""):
    table_name = table_class.hive_table_name if catalog_name == "hive_metastore" else table_class.table_name
    print(f"\nProcessing data file for Table: {table_name}\n")
    print(f"data source: {file_path}\n")
    # Create Spark DataFrame
    df = create_dataframe(spark, file_path) if not file_content else create_csv_dataframe(spark, file_content)
    file_arrival_date = "-".join(file_path.split("/")[-4:-1])
    df = df.withColumn("file_arrival_date", f.lit(file_arrival_date))
    # Reformat the df to cast the fields with the expected datatype as stated in the table spark schema
    df, schema_report = reformat_df_data_field_types2(df, table_class)
    # Create table is not exist and insert dataframe into table
    if catalog_name == "hive_metastore":
        if not table_equals_defined_schema(spark, table_name, table_class):
            spark.sql(f"DROP TABLE IF EXISTS {table_name}")
        create_table_sql = table_class.create_table().replace("MASK mask_pii", "").replace(table_class.table_name, table_name)
    else:
        create_table_sql = table_class.create_table()
    spark.sql(create_table_sql)
    df.select(table_class.get_spark_schema().names).write.insertInto(table_name, overwrite=overwrite)

    return schema_report
