from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns

db_name = "general"


def get_data_lineage(table_name):
    return {
        'target_type': "lakehouse",
        'target_endpoint': table_name,
        'src0_type': "s3",
        'src0_endpoint': "landing/reported_issues",
        'etl_script_path': "ETL/scripts/reported_issues/all_reported_issues.py",
        'src1_type': "service, kafka",
        'src1_endpoint': "ms-datalake-connector",
        'src1_script_path': "src/main/kotlin/com/ytree/msdatalakeconnector/adapter/driver/kafka/listener/ReportIssueEventListener.kt",
        'src2_type': "kafka",
        'src2_endpoint': "MS_DATALAKE_CONNECTOR_REPORT_ISSUE_EVENT_TOPIC",
        'src2_script_path': ""
    }


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


class ReportedIssuesTable(TablesDynamic):

    def __init__(self):
        self.table_name = f"{db_name}.reported_issues"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("category", StringType()),
            StructField("description", StringType()),
            StructField("client_id", StringType()),
            StructField("mobile_user_id", StringType()),
            StructField("bo_user_id", StringType()),
            StructField("time", TimestampType()),
            StructField("page_type", StringType()),
            StructField("page_url", StringType()),
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
