from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema

db_name = "logging"


class TablesDynamic(ABC):
    @abstractmethod
    def create_table(self):
        raise NotImplementedError

    @staticmethod
    def get_spark_schema():
        raise NotImplementedError

    @abstractmethod
    def delete_table(self):
        raise NotImplementedError


class GeneralInfoTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "general_info"
        self.table_name = f"{db_name}.{self.file_tag}"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        return StructType([
            StructField("etl_data", StringType()),
            StructField("date_executed", DateType()),
            StructField("start_time", TimestampType()),
            StructField("end_time", TimestampType()),
            StructField("get_data_sources_duration_secs", DoubleType()),
            StructField("total_duration_secs", DoubleType()),
            StructField("status", StringType()),
            StructField("traceback", StringType()),
            StructField("data_source", StringType()),
            StructField("data_source_type", StringType()),
            StructField("file_size_byte", StringType()),
            StructField("script_path", StringType()),
            StructField("notebook_root_id", StringType()),
            StructField("notebook_current_run_id", StringType()),
            StructField("notebook_job_group", StringType()),
            StructField("preprocess_duration_secs", DoubleType()),
        ])

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class DatabricksExecuteTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "databricks_execute"
        self.table_name = f"{db_name}.{self.file_tag}"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        return StructType([
            StructField("date_executed", DateType()),
            StructField("start_time", TimestampType()),
            StructField("end_time", TimestampType()),
            StructField("total_duration_secs", DoubleType()),
            StructField("status", StringType()),
            StructField("traceback", StringType()),
            StructField("script_path", StringType()),
            StructField("notebook_root_id", StringType()),
            StructField("notebook_current_run_id", StringType()),
            StructField("notebook_job_group", StringType()),
        ])

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class QueryLogTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "query_log"
        self.table_name = f"{db_name}.{self.file_tag}"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        return StructType([
            StructField("query_source", StringType()),
            StructField("date_executed", DateType()),
            StructField("start_time", TimestampType()),
            StructField("end_time", TimestampType()),
            StructField("total_duration_secs", DoubleType()),
            StructField("status", StringType()),
            StructField("traceback", StringType()),
            StructField("script_path", StringType()),
            StructField("query", StringType()),
        ])

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
