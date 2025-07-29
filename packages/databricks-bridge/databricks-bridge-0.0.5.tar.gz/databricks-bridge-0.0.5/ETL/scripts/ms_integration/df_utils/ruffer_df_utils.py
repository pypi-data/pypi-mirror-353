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


class RufferTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "dd/MM/yyyy"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "holdings":
            self.table_tag = file_tag
        elif file_tag in ["transactions", "cashtransactions"]:
            self.table_tag = file_tag
            self.date_format = {"*": "dd/MM/yyyy HH:mm:ss"}
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.ruffer_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/ruffer"
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
            StructField("portfolio", StringType()),
            StructField("account_number", StringType()),  # LongType()
            StructField("account_type", StringType()),
            StructField("statementdate", DateType()),
            StructField("account_base_currency", StringType()),
            StructField("asset_class", StringType()),
            StructField("asset_name", StringType()),
            StructField("sedol", StringType()),
            StructField("isin", StringType()),
            StructField("rufferinstrumentcode", StringType()),
            StructField("quantity", DoubleType()),
            StructField("cleanprice", DoubleType()),
            StructField("total_value", DoubleType()),
        ]),
        "transactions": StructType([
            StructField("portfolio", StringType()),
            StructField("account_number", StringType()),
            StructField("account_type", StringType()),
            StructField("trade_date", TimestampType()),
            StructField("transaction_type", StringType()),
            StructField("settlement_date", TimestampType()),
            StructField("asset_currency", StringType()),
            StructField("account_base_currency", StringType()),
            StructField("asset_name", StringType()),
            StructField("sedol", StringType()),
            StructField("isin", StringType()),
            StructField("rufferinstrumentcode", StringType()),
            StructField("quantity", DoubleType()),
            StructField("dividend", DoubleType()),
            StructField("price", DoubleType()),
        ]),
        "cashtransactions": StructType([
            StructField("portfolio_code", StringType()),
            StructField("portfolio_name", StringType()),
            StructField("account_number", LongType()),
            StructField("client_code", StringType()),
            StructField("cash_account_code", StringType()),
            StructField("cash_account_currency", StringType()),
            StructField("trade_date", TimestampType()),
            StructField("settlement_date", TimestampType()),
            StructField("transaction_type", StringType()),
            StructField("details", StringType()),
            StructField("cash_sign", LongType()),
            StructField("quantity", DoubleType()),
            StructField("quantity_signed", DoubleType()),
            StructField("unit", LongType()),
            StructField("book_cost", DoubleType()),
            StructField("rolling_book_cost", DoubleType()),
            StructField("source_asset_sedol", LongType()),
            StructField("source_asset_currency", StringType()),
            StructField("style_code", StringType()),
            StructField("cash_flow", DoubleType()),
            StructField("cash_flow_base_currency", DoubleType()),
            StructField("transaction_group_code", LongType()),
        ]),
    }

    return spark_schema_dict[table_tag]
