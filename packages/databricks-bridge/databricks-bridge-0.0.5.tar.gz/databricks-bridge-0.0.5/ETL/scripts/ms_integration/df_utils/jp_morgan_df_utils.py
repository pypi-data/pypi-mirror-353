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


class JPMorganTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = "\t"
        self.file_tag = file_tag
        self.date_format = {"*": "dd-MM-yyyy"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "holdings":
            self.table_tag = file_tag
        elif file_tag == "transactions":
            self.table_tag = file_tag
        elif file_tag == "instruments":
            self.table_tag = file_tag
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.jp_morgan_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/jp_morgan"
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
            StructField("reference_date", DateType()),
            StructField("account_number", StringType()),  # LongType()
            StructField("base_currency", StringType()),
            StructField("type_of_holding", StringType()),
            StructField("instrument_type_description", StringType()),
            StructField("instrument_short_name", StringType()),
            StructField("isin", StringType()),
            StructField("currency_of_instrument", StringType()),
            StructField("fx_buying_ccy", StringType()),  # *
            StructField("fx_selling_ccy", StringType()),  # *
            StructField("quantity", DoubleType()),
            StructField("price", DoubleType()),
            StructField("position_to_base_fx_rate", DoubleType()),
            StructField("buy_to_base_fx_rate", StringType()),  # *
            StructField("sell_to_base_fx_rate", StringType()),  # *
            StructField("market_value", DoubleType()),
            StructField("base_market_value", DoubleType()),
            StructField("fx_buy_amount", StringType()),  # *
            StructField("fx_sell_amount", StringType()),  # *
            StructField("fx_buy_amount_in_base", StringType()),  # *
            StructField("fx_sell_amount_in_base", StringType()),  # *
            StructField("accrued_interest", DoubleType()),
            StructField("maturity_date", DateType()),
            StructField("start_date", DateType()),
            StructField("interest_rate", DoubleType()),
            StructField("fx_deal_rate", StringType()),  # *
            StructField("last_fx_rate", StringType()),  # *
            StructField("account_name", StringType()),
            StructField("iban", StringType()),
            StructField("full_account_number", StringType()),
            StructField("instrument_type_code", StringType()),  # LongType()
            StructField("instrument_long_name", StringType()),
            StructField("valoren", StringType()),
            StructField("valoren_suffix", StringType()),
            StructField("cusip", StringType()),
            StructField("sedol", StringType()),
            StructField("bloomberg_ticker", StringType()),  # *
            StructField("base_price", DoubleType()),
            StructField("date_of_price", DateType()),
            StructField("base_accrued_interest", DoubleType()),
            StructField("average_cost_amount", DoubleType()),
            StructField("average_cost_price", DoubleType()),
            StructField("average_cost_amount_in_base", DoubleType()),
            StructField("average_cost_price_in_base", DoubleType()),
            StructField("average_bought_amount", DoubleType()),
            StructField("average_bought_price", DoubleType()),
            StructField("average_bought_amount_in_base", DoubleType()),
            StructField("average_bought_price_in_base", DoubleType()),
            StructField("country_of_instrument", StringType()),
            StructField("exchange_rate_date", DateType()),
            StructField("income_currency", StringType()),
            StructField("income_frequency", StringType()),  # IntegerType()
            StructField("date_of_last_income", DateType()),
            StructField("marketplace", StringType()),
            StructField("asset_classification1", StringType()),
            StructField("asset_classification2", StringType()),
            StructField("asset_classification3", StringType()),
            StructField("current_face", DoubleType()),
            StructField("factor", DoubleType()),
            StructField("custodian_id", StringType()),  # LongType()
            StructField("custodian_name", StringType()),
            StructField("fx_rate_platform_ccy", DoubleType()),
            StructField("collateral_amount_base_ccy_lending_value", DoubleType()),
            StructField("collateral_amount_position_ccy_lending_value", DoubleType()),
            StructField("contract_id", StringType()),
        ]),
        "transactions": StructType([
            StructField("from_date", DateType()),
            StructField("to_date", DateType()),
            StructField("account_number", StringType()),  # LongType()
            StructField("type_of_transaction", StringType()),
            StructField("instrument_type_description", StringType()),
            StructField("transaction_number", StringType()),
            StructField("olympic_transaction_code", StringType()),
            StructField("transaction_description", StringType()),
            StructField("instrument_short_name", StringType()),
            StructField("isin", StringType()),
            StructField("transaction_currency", StringType()),
            StructField("quantity", DoubleType()),
            StructField("trade_date", DateType()),
            StructField("value_date", DateType()),
            StructField("transaction_price", DoubleType()),
            StructField("transaction_to_base_fx_rate", DoubleType()),
            StructField("net_transaction_amount", DoubleType()),
            StructField("net_transaction_amount_in_base", DoubleType()),
            StructField("accrued_interest", DoubleType()),
            StructField("interest_rate", DoubleType()),
            StructField("gross_transaction_amount", DoubleType()),
            StructField("ex_date", DateType()),
            StructField("dividend_coupon_rate", DoubleType()),
            StructField("full_account_number", StringType()),
            StructField("iban", StringType()),  # *
            StructField("account_name", StringType()),
            StructField("instrument_type_code", StringType()),  # LongType()
            StructField("instrument_long_name", StringType()),
            StructField("valoren", StringType()),  # LongType()
            StructField("valoren_suffix", StringType()),
            StructField("cusip", StringType()),
            StructField("sedol", StringType()),
            StructField("ticker", StringType()),
            StructField("pricing_currency", StringType()),
            StructField("base_currency", StringType()),
            StructField("price_in_base_currency", DoubleType()),
            StructField("accrued_interest_in_base", DoubleType()),
            StructField("brokerage_fees", DoubleType()),
            StructField("counterparty_fees", DoubleType()),
            StructField("jpm_brokerage_fees", DoubleType()),
            StructField("jpm_fees", DoubleType()),
            StructField("swiss_tax", DoubleType()),
            StructField("withholding_tax", DoubleType()),
            StructField("cash_currency", StringType()),
            StructField("cash_amount", DoubleType()),
            StructField("counterparty_name", StringType()),
            StructField("reversal_flag", StringType()),  # IntegerType()
            StructField("reversal_reference", StringType()),  # IntegerType()
            StructField("marketplace", StringType()),
            StructField("asset_classification1", StringType()),
            StructField("asset_classification2", StringType()),
            StructField("asset_classification3", StringType()),
            StructField("current_face", DoubleType()),
            StructField("factor", DoubleType()),
            StructField("maturity_date", DateType()),
            StructField("payable_date", DateType()),
            StructField("contract_id", StringType()),  # *
            StructField("fx_rate_platform_ccy", DoubleType()),
            StructField("long_transaction_description", StringType()),
        ]),
        "instruments": StructType([
            StructField("reference_date", DateType()),
            StructField("kind_of_instrument", StringType()),
            StructField("instrument_type_description", StringType()),
            StructField("instrument_short_name", StringType()),
            StructField("isin", StringType()),
            StructField("instrument_currency", StringType()),
            StructField("price", DoubleType()),
            StructField("date_of_price", DateType()),
            StructField("maturity_date", DateType()),
            StructField("income_frequency", StringType()),  # IntegerType()
            StructField("asset_classification1", StringType()),
            StructField("asset_classification2", StringType()),
            StructField("asset_classification3", StringType()),
            StructField("factor", DoubleType()),
            StructField("debtor_name", StringType()),  # *
            StructField("debtor_location", StringType()),  # *
            StructField("industry_group", StringType()),
            StructField("issuer_name", StringType()),
            StructField("instrument_type_code", StringType()),  # LongType()
            StructField("instrument_long_name", StringType()),
            StructField("valoren", StringType()),
            StructField("valoren_suffix", StringType()),
            StructField("cusip", StringType()),
            StructField("sedol", StringType()),
            StructField("ric", StringType()),
            StructField("bloomberg_ticker", StringType()),
            StructField("pos_to_base_fx_rate", StringType()),
            StructField("base_price", DoubleType()),
            StructField("issue_date", DateType()),
            StructField("accrued_interest", DoubleType()),
            StructField("interest_rate", DoubleType()),
            StructField("income_ccy", StringType()),
            StructField("payment_date_of_last_income", DateType()),
            StructField("ex_date_of_last_dividend", DateType()),
            StructField("payment_date_of_next_income", DateType()),
            StructField("value_date_of_next_coupon", DateType()),
            StructField("ex_date_of_next_dividend", DateType()),
            StructField("interest_base", StringType()),
            StructField("country_of_instrument", StringType()),
            StructField("marketplace", StringType()),
        ]),
    }

    return spark_schema_dict[table_tag]
