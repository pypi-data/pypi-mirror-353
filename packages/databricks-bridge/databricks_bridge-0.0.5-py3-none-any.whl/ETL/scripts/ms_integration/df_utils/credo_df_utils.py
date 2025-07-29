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


class CredoTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "yyyy-MM-ddTHH:mm:ss.S"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "accounts":
            self.table_tag = file_tag
        elif file_tag == "positions":
            self.table_tag = file_tag
        elif file_tag == "transactions":
            self.table_tag = file_tag
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.credo_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/credo"
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
        "accounts": StructType([
            StructField("report_date", TimestampType()),
            StructField("open_date", TimestampType()),
            StructField("portfolio_number", StringType()),
            StructField("account_number", StringType()),
            StructField("external_reference", StringType()),
            StructField("account_name1", StringType()),
            StructField("account_name2", StringType()),
            StructField("account_type", StringType()),
            StructField("dealing_type", StringType()),
            StructField("risk_rating", StringType()),
            StructField("account_manager", StringType()),
            StructField("reporting_currency_iso", StringType()),
            StructField("tax_jurisdiction_iso3166", StringType()),  # *
            StructField("total_market_value", DoubleType()),
            StructField("total_cash", DoubleType()),
            StructField("total_market_value_iso", StringType()),
        ]),
        "positions": StructType([
            StructField("report_date", TimestampType()),
            StructField("portfolio_number", StringType()),
            StructField("account_number", StringType()),
            StructField("type_code", StringType()),
            StructField("symbol", StringType()),
            StructField("sedol", StringType()),
            StructField("sedol2", StringType()),
            StructField("isin", StringType()),
            StructField("ticker", StringType()),
            StructField("short_name", StringType()),
            StructField("long_name", StringType()),
            StructField("local_currency_iso", StringType()),
            StructField("quantity", DoubleType()),
            StructField("unit_cost", DoubleType()),
            StructField("book_cost", DoubleType()),
            StructField("book_cost_date", TimestampType()),
            StructField("price", DoubleType()),
            StructField("price_factor", DoubleType()),
            StructField("market_value", DoubleType()),
            StructField("reporting_market_value", DoubleType()),
            StructField("share_class", StringType()),
            StructField("fx_rate", DoubleType()),
            StructField("reporting_market_value_iso", StringType()),
            StructField("position_date", TimestampType()),
            StructField("coupon_rate", DoubleType()),
            StructField("maturity_date", TimestampType()),
        ]),
        "transactions": StructType([
            StructField("report_date", TimestampType()),
            StructField("portfolio_number", StringType()),
            StructField("account_number", StringType()),
            StructField("type_code", StringType()),
            StructField("symbol", StringType()),
            StructField("sedol", StringType()),
            StructField("sedol2", StringType()),  # *
            StructField("isin", StringType()),
            StructField("ticker", StringType()),
            StructField("transaction_reference", StringType()),  # LongType()
            StructField("tran_code", StringType()),
            StructField("transaction_type", StringType()),
            StructField("trade_date", TimestampType()),
            StructField("settlement_date", TimestampType()),
            StructField("quantity", DoubleType()),
            StructField("net_price", StringType()),  # *
            StructField("net_amount", DoubleType()),
            StructField("accrued_interest", StringType()),  # *
            StructField("accrued_interest_day_count", StringType()),  # *
            StructField("trade_date_fx", StringType()),  # *
            StructField("settlement_date_fx", StringType()),  # *
            StructField("settlement_currency_iso", StringType()),
            StructField("settlement_cash_account", StringType()),
            StructField("broker_commission", StringType()),  # *
            StructField("commission", StringType()),  # *
            StructField("implied_commission", StringType()),  # *
            StructField("tax", StringType()),  # *
            StructField("withholding_tax", DoubleType()),
            StructField("exchange_fee", StringType()),  # *
            StructField("ticket_charge", StringType()),  # *
            StructField("settlement_fee", StringType()),  # *
            StructField("ptm_levy", StringType()),  # *
            StructField("stamp_duty", StringType()),  # *
            StructField("fees", StringType()),  # *
            StructField("venue_mic", StringType()),
            StructField("book_cost", DoubleType()),
            StructField("book_cost_date", TimestampType()),
            StructField("market_value", DoubleType()),
            StructField("mark_to_market", StringType()),
            StructField("comment", StringType()),
            StructField("reversal_flag", StringType()),
            StructField("short_name", StringType()),
            StructField("long_name", StringType()),
        ]),
    }

    return spark_schema_dict[table_tag]
