from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns

db_name = "profiles"
data_source = "pod"


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


class PodPTTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "pt"
        self.table_name = f"{db_name}.{data_source}_{self.file_tag}"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField('client_id', StringType()),
            StructField('pod_id', StringType()),
            StructField('pod', StringType()),
            StructField('data_dt', DateType())
        ])
        return non_essentialize_all_other_columns(schema)
        
    def delete_table(self):
        return f'''DROP TABLE IF EXISTS {self.table_name};'''