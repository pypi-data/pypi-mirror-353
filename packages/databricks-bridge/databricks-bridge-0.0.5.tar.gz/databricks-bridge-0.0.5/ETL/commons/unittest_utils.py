from ETL.commons.start_spark_session import get_or_create_spark_session
import tempfile
import os
import uuid

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType, StructField


def get_spark_session():
    spark, _, _ = get_or_create_spark_session()
    return spark


def create_tempfile_from_string_data(bytes_str_data: bytes, env: dict = None) -> str:
    """
    :param env:
    :param bytes_str_data:
    :return temp file filepath string:
    """
    file_path = ""
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        env["dbutils"].fs.mkdirs("/tmp")
        file_path = f"/dbfs/tmp/{uuid.uuid1()}"
        with open(file_path, "wb") as f:
            f.write(bytes_str_data)
    else:
        tp = tempfile.NamedTemporaryFile(delete=False)
        tp.write(bytes_str_data)
        tp.close()
        file_path = tp.name

    return file_path


def update_df_column_nullability(spark: SparkSession, df: DataFrame, col_name: str, nullability: bool):
    new_schema = StructType([
        StructField(field.name, field.dataType, nullability) if field.name == col_name else field
        for field in df.schema.fields
    ])
    return spark.createDataFrame(df.rdd, new_schema)
