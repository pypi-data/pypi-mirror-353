from pyspark.sql import SparkSession
from datetime import datetime, date

from ETL.commons.spark_table_utils import create_dataframe_with_dict_list
from ETL.logging.df_utils.logging_df_utils import QueryLogTable, db_name


class QueryLogger:
    def __init__(self, spark: SparkSession, query_source: str):
        self.query_source = query_source
        self.spark = spark
        # spark.sql(f"drop database if exists {db_name} cascade;")
        self.spark.sql(f"create database if not exists {db_name};")
        # Create table is not exist and insert dataframe into table
        self.table_class = QueryLogTable()
        self.spark.sql(self.table_class.create_table())

    def insert_log_into_table(
            self, script_path: str, query: str, success: bool, start_time: datetime,
            end_time: datetime, traceback: str = None
    ):
        date_executed = start_time.date()
        datetime_diff = end_time - start_time
        duration_s = datetime_diff.total_seconds()
        dict_list = [{
            "query_source": self.query_source, "query": query, "status": "success" if success else "fail",
            "date_executed": date_executed, "start_time": start_time, "end_time": end_time,
            "total_duration_secs": duration_s, "traceback": traceback, "script_path": script_path
        }]
        df = create_dataframe_with_dict_list(self.spark, dict_list, self.table_class.get_spark_schema())
        df.write.insertInto(self.table_class.table_name, overwrite=False)
