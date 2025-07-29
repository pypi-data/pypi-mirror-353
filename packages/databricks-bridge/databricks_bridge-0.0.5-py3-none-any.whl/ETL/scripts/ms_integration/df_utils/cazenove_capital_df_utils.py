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

    @abstractmethod
    def get_spark_schema(self):
        raise NotImplementedError

    @abstractmethod
    def delete_table(self):
        raise NotImplementedError


class CazenoveCapitalTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "dd/MM/yyyy"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "val":
            self.table_tag = "holdings"
        elif file_tag == "trans":
            self.table_tag = "transactions"
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.cazenove_capital_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/cazenove_capital"
        etl_path = "ETL/scripts/ms_integration/all_ms_integration_csv_txt.py"
        self.data_lineage = get_data_lineage(self.table_name, s3_endpoint, etl_path)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    def get_spark_schema(self):
        return non_essentialize_all_other_columns(get_table_schema(self.table_tag))

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


def get_table_schema(table_tag: str) -> StructType:
    spark_schema_dict = {
        "holdings": StructType([
            StructField("relationship_number", StringType()),
            StructField("account_number", StringType()),
            StructField("account_type", StringType()),
            StructField("statement_date", DateType()),
            StructField("account_base_currency", StringType()),
            StructField("asset_name", StringType()),
            StructField("isin_asset_id_cash", StringType()),
            StructField("quantity", DoubleType()),
            StructField("market_price", DoubleType()),
            StructField("market_price_currency", StringType()),
            StructField("value_date", DateType()),
            StructField("total_value", DoubleType()),
            StructField("cost_basis", DoubleType()),
        ]),
        "transactions": StructType([
            StructField("transaction_date", DateType()),
            StructField("relationship_number", StringType()),
            StructField("account_number", StringType()),
            StructField("transaction_type", StringType()),
            StructField("transaction_code", StringType()),  # *
            StructField("transaction_amount", DoubleType()),
            StructField("debit_credit", StringType()),
            StructField("transaction_currency", StringType()),
            StructField("transaction_description", StringType()),
            StructField("cancel", StringType()),
            StructField("trans_ref", StringType()),
            StructField("type", StringType()),
        ])
    }

    return spark_schema_dict[table_tag]
