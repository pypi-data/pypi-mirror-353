from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns


def get_data_lineage(table_name, s3_endpoint, etl_path):
    return {
        'target_type': "lakehouse",
        'target_endpoint': table_name,
        'src0_type': "s3",
        'src0_endpoint': s3_endpoint,
        'etl_script_path': etl_path,
        'src1_type': "service",
        'src1_endpoint': "ms-datalake-connector",
        'src1_script_path': "src/main/kotlin/com/ytree/msdatalakeconnector/adapter/driver/kafka/listener/FinancialStatementEventListener.kt",
        'src2_type': "kafka",
        'src2_endpoint': "MS_DATALAKE_CONNECTOR_FINANCIALSTATEMENT_EVENT_TOPIC",
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


class HedgeservTable(TablesDynamic):

    def __init__(self, db_name):
        self.sep = ","
        self.date_format = {"*": "M/dd/yyyy"}
        self.column_line_index = 0
        self.column_line = []
        self.table_name = f"{db_name}.hedgeserv"
        s3_endpoint = "landing/financial_statement/ms-integration/hedgeserv"
        etl_path = "ETL/scripts/ms_integration/all_ms_integration_csv_txt.py"
        self.data_lineage = get_data_lineage(self.table_name, s3_endpoint, etl_path)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("fund_code", StringType()),
            StructField("investor_id", StringType()),  # LongType()
            StructField("statement_date", DateType()),
            StructField("ccy", StringType()),
            StructField("subscriptions", StringType()),  # LongType()
            StructField("redemptions", StringType()),  # LongType()
            StructField("transfers", StringType()),  # LongType()
            StructField("end_net_capital_local", DoubleType()),
            StructField("nnav_sh", DoubleType()),
            StructField("ending_shares", DoubleType()),
            StructField("master_investor_id", StringType()),  # LongType()
            StructField("fund_id", StringType()),  # LongType()
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
