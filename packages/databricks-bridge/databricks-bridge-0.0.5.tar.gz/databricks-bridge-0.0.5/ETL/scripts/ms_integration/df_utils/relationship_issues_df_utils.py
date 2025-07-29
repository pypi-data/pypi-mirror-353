from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns

db_name = "ms_integration"
etl_data_name = "relationship_issues"
permitted_groups = ["analysts"]


def get_data_lineage(table_name):
    return {
        'target_type': "lakehouse",
        'target_endpoint': table_name,
        'src0_type': "s3",
        'src0_endpoint': "landing/financial_statement/relationship-issues/json/no-relationship",
        'etl_script_path': "ETL/scripts/ms_integration/relationship_issues_etl.py",
        'src1_type': "service",
        'src1_endpoint': "ms-datalake-connector",
        'src1_script_path': "src/main/kotlin/com/ytree/msdatalakeconnector/adapter/driver/kafka/listener/ReportIssueEventListener.kt",
        'src2_type': "kafka",
        'src2_endpoint': "MS_DATALAKE_CONNECTOR_FINANCIALSTATEMENT_EVENT_TOPIC",
        'src2_script_path': ""
    }


class TablesDynamic(ABC):
    @abstractmethod
    def create_table(self):
        raise NotImplementedError

    @abstractmethod
    def get_spark_schema(self):
        raise NotImplementedError

    @abstractmethod
    def delete_table(self):
        raise NotImplementedError


class RelationshipIssuesTable(TablesDynamic):

    def __init__(self):
        self.table_name = f"{db_name}.relationship_issues"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    def get_spark_schema(self):
        schema = StructType([
            StructField("provider_name", StringType()),
            StructField("provider_id", StringType()),
            StructField("relationship_number", StringType()),
            StructField("effective_date", DateType()),
            StructField("relationship_status", StringType()),
            StructField("error_message", StringType()),
            StructField("insert_timestamp", TimestampType()),
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
