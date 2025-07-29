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


class RothschildTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ";"
        self.file_tag = file_tag
        self.date_format = {"*": "dd.MM.yyyy"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "positions":
            self.table_tag = file_tag
        elif file_tag == "cash":
            self.table_tag = file_tag
        elif file_tag == "asset":
            self.table_tag = file_tag
        elif file_tag == "securities":
            self.table_tag = file_tag
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.rothschild_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/rothschild"
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
        "positions": StructType([
            StructField("valuation_date", DateType()),
            StructField("portfolio", DoubleType()),
            StructField("asset_class", StringType()),
            StructField("quantity", StringType()),
            StructField("position_currency", StringType()),
            StructField("asset", StringType()),
            StructField("isin", StringType()),
            StructField("valoren", StringType()),  # LongType()
            StructField("maturity_date", DateType()),
            StructField("price_currency", StringType()),
            StructField("price", DoubleType()),
            StructField("fx_rate", DoubleType()),
            StructField("market_value_in_position_currency", StringType()),
            StructField("book_cost_in_portfolio_currency", StringType()),
            StructField("accrued_interest_in_portfolio_currency", StringType()),
            StructField("market_value_in_portfolio_currency", StringType()),
            StructField("portfolio_currency", StringType()),
            StructField("percent_of_assets", StringType()),
            StructField("ytm_percent", StringType()),
            StructField("modified_duration", StringType()),
            # StructField("", StringType()),
        ]),
        "cash": StructType([
            StructField("portfolio", DoubleType()),
            StructField("trade_date", DateType()),
            StructField("value_date", DateType()),
            StructField("transaction_type", StringType()),
            StructField("order_type", StringType()),
            StructField("order_number", StringType()),  # LongType()
            StructField("status", StringType()),
            StructField("movement_description", StringType()),
            StructField("isin", StringType()),
            StructField("cash_account_type", StringType()),
            StructField("amount", StringType()),
        ]),
        "asset": StructType([
            StructField("asset", StringType()),
            StructField("valoren_number", StringType()),  # LongType()
            StructField("isin", StringType()),
            StructField("instrument_group", StringType()),
            StructField("asset_type", StringType()),
            StructField("currency", StringType()),
            StructField("rating_s_and_p", StringType()),  # *
            StructField("rating_moody", StringType()),  # *
        ]),
        "securities": StructType([
            StructField("portfolio", DoubleType()),
            StructField("portfolio_currency", StringType()),
            StructField("trade_date", DateType()),
            StructField("value_date", DateType()),
            StructField("asset_name", StringType()),
            StructField("valoren_number", StringType()),  # LongType()
            StructField("isin", StringType()),
            StructField("position_currency", StringType()),
            StructField("order_number", StringType()),  # LongType()
            StructField("status", StringType()),
            StructField("movement_description", StringType()),
            StructField("price_in_position_currency", DoubleType()),
            StructField("quantity", DoubleType()),
            StructField("net_value_in_position_currency", DoubleType()),
            StructField("fx_rate_from_position_currency_to_portfolio_currency", StringType()),  # IntegerType()
            StructField("net_value_in_portfolio_currency", DoubleType()),
            StructField("accrued_interest", StringType()),  # *
            StructField("transaction_type", StringType()),
            StructField("order_type", StringType()),
            StructField("deal_fwd_rate", StringType()),  # *
            StructField("cost", DoubleType()),
            StructField("booking_kind", StringType()),
            StructField("amount", DoubleType()),
            StructField("charging", StringType()),
        ]),
    }

    return spark_schema_dict[table_tag]
