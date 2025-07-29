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


class UBSTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ";"
        self.file_tag = file_tag
        self.date_format = {"*": "yyyyMMdd"}
        self.column_line_index = 7
        self.column_line = []

        if file_tag == "zah":
            self.table_tag = "holdings"
        elif file_tag == "zaq":
            self.table_tag = "cash"
            self.date_format = {"closing_balance_value_date": "yyMMdd",
                                "closing_available_bal_settld_value_date": "yyMMdd",

                                "redemption_date": "yyyyMMdd"}
        elif file_tag == "zad":
            self.table_tag = "transactions"
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.ubs_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/ubs"
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
            StructField("page_number", StringType()),  # IntegerType()
            StructField("continuation_indicator", StringType()),
            StructField("senders_reference_number", StringType()),
            StructField("function_of_the_message", StringType()),
            StructField("subfunction", StringType()),  # *
            StructField("preparation_date", DateType()),
            StructField("preparation_time", StringType()),
            StructField("statement_date", DateType()),
            StructField("statement_frequency_indicator", StringType()),
            StructField("complete_updates_indicator", StringType()),
            StructField("statement_type", StringType()),
            StructField("statement_basis", StringType()),
            StructField("account_owner_dss", StringType()),
            StructField("account_owner_code", StringType()),  # LongType()
            StructField("safekeeping_account", StringType()),  # LongType()
            StructField("activity_flag", StringType()),
            StructField("sub_safekeeping_statement", StringType()),
            StructField("total_holdings_value_of_statement_currency_code", StringType()),
            StructField("total_holdings_value_of_statement_amount", StringType()),  # DoubleType()
            StructField("isin_number", StringType()),
            StructField("swiss_valoren_number", StringType()),  # *
            StructField("short_description", StringType()),
            StructField("ubs_asset_code", StringType()),  # LongType()
            StructField("aggregate_balance_code_current", StringType()),
            StructField("aggregate_balance_amount_current", StringType()),  # DoubleType()
            StructField("aggregate_balance_amount_amortized", StringType()),  # *
            StructField("available_balance_code", StringType()),
            StructField("available_balance_amount", StringType()),  # DoubleType()
            StructField("not_available_balance_code", StringType()),
            StructField("not_available_balance_amount", StringType()),  # DoubleType()
            StructField("holding_value_currency_code_position", StringType()),
            StructField("holding_value_amount_position", StringType()),  # LongType()
            StructField("reference_currency_code", StringType()),
            StructField("reference_currency_exchange_rate_to_base_currency", DoubleType()),
            StructField("not_realized_market_value_profit_currency_code_position", StringType()),  # *
            StructField("not_realized_market_value_profit_amount_position", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_currency_code_position", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_amount_position", StringType()),  # *
            StructField("not_realized_total_profit_currency_code_position", StringType()),  # *
            StructField("not_realized_total_profit_amount_position", StringType()),  # *
            StructField("balance_qualifier_subbal1", StringType()),
            StructField("balance_description_subbal1", StringType()),
            StructField("balance_type_code_subbal1", StringType()),
            StructField("balance_available_code_subbal1", StringType()),  # *
            StructField("balance_amount_subbal1", StringType()),  # DoubleType()
            StructField("source_of_price_subbal1", StringType()),  # *
            StructField("place_of_safekeeping_code_subbal1", StringType()),  # LongType()
            StructField("place_of_safekeeping_bicsubbal1", StringType()),
            StructField("place_of_safekeeping_country_code_subbal1", StringType()),
            StructField("market_price_type_code_subbal1", StringType()),
            StructField("market_price_currency_code_subbal1", StringType()),
            StructField("market_price_value_subbal1", DoubleType()),
            StructField("price_quotation_date_subbal1", DateType()),
            StructField("number_of_days_accrued_subbal1", StringType()),  # LongType()
            StructField("holding_value_currency_code_subbal1", StringType()),
            StructField("holding_value_amount_subbal1", StringType()),  # DoubleType()
            StructField("accrued_interest_currency_code_subbal1", StringType()),
            StructField("accrued_interest_amount_subbal1", StringType()),  # DoubleType()
            StructField("book_value_currency_code_subbal1", StringType()),  # *
            StructField("book_value_amount_subbal1", StringType()),  # *
            StructField("exchange_rate_first_currency_code_subbal1", StringType()),  # *
            StructField("exchange_rate_second_currency_code_subbal1", StringType()),  # *
            StructField("exchange_rate_value_subbal1", StringType()),  # *
            StructField("security_currency_code_subbal1", StringType()),
            StructField("security_currency_exchange_rate_to_base_currency_subbal1", DoubleType()),
            StructField("cost_price_currency_code_subbal1", StringType()),  # *
            StructField("cost_price_amount_subbal1", StringType()),  # *
            StructField("not_realized_market_value_profit_currency_code_subbal1", StringType()),  # *
            StructField("not_realized_market_value_profit_amount_subbal1", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_currency_code_subbal1", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_amount_subbal1", StringType()),  # *
            StructField("alternate_id", StringType()),  # *
            StructField("place_of_safekeeping_subbal1", StringType()),  # *
            StructField("balance_qualifier_subbal2", StringType()),  # *
            StructField("balance_description_subbal2", StringType()),  # *
            StructField("balance_type_code_subbal2", StringType()),  # *
            StructField("balance_available_code_subbal2", StringType()),  # *
            StructField("balance_amount_subbal2", StringType()),  # *
            StructField("source_of_price_subbal2", StringType()),  # *
            StructField("place_of_safekeeping_code_subbal2", StringType()),  # *
            StructField("place_of_safekeeping_bicsubbal2", StringType()),  # *
            StructField("place_of_safekeeping_country_code_subbal2", StringType()),  # *
            StructField("market_price_type_code_subbal2", StringType()),  # *
            StructField("market_price_currency_code_subbal2", StringType()),  # *
            StructField("market_price_value_subbal2", StringType()),  # *
            StructField("price_quotation_date_subbal2", StringType()),  # *
            StructField("number_of_days_accrued_subbal2", StringType()),  # *
            StructField("holding_value_currency_code_subbal2", StringType()),  # *
            StructField("holding_value_amount_subbal2", StringType()),  # *
            StructField("accrued_interest_currency_code_subbal2", StringType()),  # *
            StructField("accrued_interest_amount_subbal2", StringType()),  # *
            StructField("book_value_currency_code_subbal2", StringType()),  # *
            StructField("book_value_amount_subbal2", StringType()),  # *
            StructField("exchange_rate_first_currency_code_subbal2", StringType()),  # *
            StructField("exchange_rate_second_currency_code_subbal2", StringType()),  # *
            StructField("exchange_rate_value_subbal2", StringType()),  # *
            StructField("security_currency_code_subbal2", StringType()),  # *
            StructField("security_currency_exchange_rate_to_base_currency_subbal2", StringType()),  # *
            StructField("cost_price_currency_code_subbal2", StringType()),  # *
            StructField("cost_price_amount_subbal2", StringType()),  # *
            StructField("not_realized_market_value_profit_currency_code_subbal2", StringType()),  # *
            StructField("not_realized_market_value_profit_amount_subbal2", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_currency_code_subbal2", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_amount_subbal2", StringType()),  # *
            StructField("place_of_safekeeping_subbal2", StringType()),  # *
            StructField("balance_qualifier_subbal3", StringType()),  # *
            StructField("balance_description_subbal3", StringType()),  # *
            StructField("balance_type_code_subbal3", StringType()),  # *
            StructField("balance_available_code_subbal3", StringType()),  # *
            StructField("balance_amount_subbal3", StringType()),  # *
            StructField("source_of_price_subbal3", StringType()),  # *
            StructField("place_of_safekeeping_code_subbal3", StringType()),  # *
            StructField("place_of_safekeeping_bicsubbal3", StringType()),  # *
            StructField("place_of_safekeeping_country_code_subbal3", StringType()),  # *
            StructField("market_price_type_code_subbal3", StringType()),  # *
            StructField("market_price_currency_code_subbal3", StringType()),  # *
            StructField("market_price_value_subbal3", StringType()),  # *
            StructField("price_quotation_date_subbal3", StringType()),  # *
            StructField("number_of_days_accrued_subbal3", StringType()),  # *
            StructField("holding_value_currency_code_subbal3", StringType()),  # *
            StructField("holding_value_amount_subbal3", StringType()),  # *
            StructField("accrued_interest_currency_code_subbal3", StringType()),  # *
            StructField("accrued_interest_amount_subbal3", StringType()),  # *
            StructField("book_value_currency_code_subbal3", StringType()),  # *
            StructField("book_value_amount_subbal3", StringType()),  # *
            StructField("exchange_rate_first_currency_code_subbal3", StringType()),  # *
            StructField("exchange_rate_second_currency_code_subbal3", StringType()),  # *
            StructField("exchange_rate_value_subbal3", StringType()),  # *
            StructField("security_currency_code_subbal3", StringType()),  # *
            StructField("security_currency_exchange_rate_to_base_currency_subbal3", StringType()),  # *
            StructField("cost_price_currency_code_subbal3", StringType()),  # *
            StructField("cost_price_amount_subbal3", StringType()),  # *
            StructField("not_realized_market_value_profit_currency_code_subbal3", StringType()),  # *
            StructField("not_realized_market_value_profit_amount_subbal3", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_currency_code_subbal3", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_amount_subbal3", StringType()),  # *
            StructField("place_of_safekeeping_subbal3", StringType()),  # *
            StructField("balance_qualifier_subbal4", StringType()),  # *
            StructField("balance_description_subbal4", StringType()),  # *
            StructField("balance_type_code_subbal4", StringType()),  # *
            StructField("balance_available_code_subbal4", StringType()),  # *
            StructField("balance_amount_subbal4", StringType()),  # *
            StructField("source_of_price_subbal4", StringType()),  # *
            StructField("place_of_safekeeping_code_subbal4", StringType()),  # *
            StructField("place_of_safekeeping_bicsubbal4", StringType()),  # *
            StructField("place_of_safekeeping_country_code_subbal4", StringType()),  # *
            StructField("market_price_type_code_subbal4", StringType()),  # *
            StructField("market_price_currency_code_subbal4", StringType()),  # *
            StructField("market_price_value_subbal4", StringType()),  # *
            StructField("price_quotation_date_subbal4", StringType()),  # *
            StructField("number_of_days_accrued_subbal4", StringType()),  # *
            StructField("holding_value_currency_code_subbal4", StringType()),  # *
            StructField("holding_value_amount_subbal4", StringType()),  # *
            StructField("accrued_interest_currency_code_subbal4", StringType()),  # *
            StructField("accrued_interest_amount_subbal4", StringType()),  # *
            StructField("book_value_currency_code_subbal4", StringType()),  # *
            StructField("book_value_amount_subbal4", StringType()),  # *
            StructField("exchange_rate_first_currency_code_subbal4", StringType()),  # *
            StructField("exchange_rate_second_currency_code_subbal4", StringType()),  # *
            StructField("exchange_rate_value_subbal4", StringType()),  # *
            StructField("security_currency_code_subbal4", StringType()),  # *
            StructField("security_currency_exchange_rate_to_base_currency_subbal4", StringType()),  # *
            StructField("cost_price_currency_code_subbal4", StringType()),  # *
            StructField("cost_price_amount_subbal4", StringType()),  # *
            StructField("not_realized_market_value_profit_currency_code_subbal4", StringType()),  # *
            StructField("not_realized_market_value_profit_amount_subbal4", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_currency_code_subbal4", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_amount_subbal4", StringType()),  # *
            StructField("place_of_safekeeping_subbal4", StringType()),  # *
            StructField("balance_qualifier_subbal5", StringType()),  # *
            StructField("balance_description_subbal5", StringType()),  # *
            StructField("balance_type_code_subbal5", StringType()),  # *
            StructField("balance_available_code_subbal5", StringType()),  # *
            StructField("balance_amount_subbal5", StringType()),  # *
            StructField("source_of_price_subbal5", StringType()),  # *
            StructField("place_of_safekeeping_code_subbal5", StringType()),  # *
            StructField("place_of_safekeeping_bicsubbal5", StringType()),  # *
            StructField("place_of_safekeeping_country_code_subbal5", StringType()),  # *
            StructField("market_price_type_code_subbal5", StringType()),  # *
            StructField("market_price_currency_code_subbal5", StringType()),  # *
            StructField("market_price_value_subbal5", StringType()),  # *
            StructField("price_quotation_date_subbal5", StringType()),  # *
            StructField("number_of_days_accrued_subbal5", StringType()),  # *
            StructField("holding_value_currency_code_subbal5", StringType()),  # *
            StructField("holding_value_amount_subbal5", StringType()),  # *
            StructField("accrued_interest_currency_code_subbal5", StringType()),  # *
            StructField("accrued_interest_amount_subbal5", StringType()),  # *
            StructField("book_value_currency_code_subbal5", StringType()),  # *
            StructField("book_value_amount_subbal5", StringType()),  # *
            StructField("exchange_rate_first_currency_code_subbal5", StringType()),  # *
            StructField("exchange_rate_second_currency_code_subbal5", StringType()),  # *
            StructField("exchange_rate_value_subbal5", StringType()),  # *
            StructField("security_currency_code_subbal5", StringType()),  # *
            StructField("security_currency_exchange_rate_to_base_currency_subbal5", StringType()),  # *
            StructField("cost_price_currency_code_subbal5", StringType()),  # *
            StructField("cost_price_amount_subbal5", StringType()),  # *
            StructField("not_realized_market_value_profit_currency_code_subbal5", StringType()),  # *
            StructField("not_realized_market_value_profit_amount_subbal5", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_currency_code_subbal5", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_amount_subbal5", StringType()),  # *
            StructField("place_of_safekeeping_subbal5", StringType()),  # *
            StructField("balance_qualifier_subbal6", StringType()),  # *
            StructField("balance_description_subbal6", StringType()),  # *
            StructField("balance_type_code_subbal6", StringType()),  # *
            StructField("balance_available_code_subbal6", StringType()),  # *
            StructField("balance_amount_subbal6", StringType()),  # *
            StructField("source_of_price_subbal6", StringType()),  # *
            StructField("place_of_safekeeping_code_subbal6", StringType()),  # *
            StructField("place_of_safekeeping_bicsubbal6", StringType()),  # *
            StructField("place_of_safekeeping_country_code_subbal6", StringType()),  # *
            StructField("market_price_type_code_subbal6", StringType()),  # *
            StructField("market_price_currency_code_subbal6", StringType()),  # *
            StructField("market_price_value_subbal6", StringType()),  # *
            StructField("price_quotation_date_subbal6", StringType()),  # *
            StructField("number_of_days_accrued_subbal6", StringType()),  # *
            StructField("holding_value_currency_code_subbal6", StringType()),  # *
            StructField("holding_value_amount_subbal6", StringType()),  # *
            StructField("accrued_interest_currency_code_subbal6", StringType()),  # *
            StructField("accrued_interest_amount_subbal6", StringType()),  # *
            StructField("book_value_currency_code_subbal6", StringType()),  # *
            StructField("book_value_amount_subbal6", StringType()),  # *
            StructField("exchange_rate_first_currency_code_subbal6", StringType()),  # *
            StructField("exchange_rate_second_currency_code_subbal6", StringType()),  # *
            StructField("exchange_rate_value_subbal6", StringType()),  # *
            StructField("security_currency_code_subbal6", StringType()),  # *
            StructField("security_currency_exchange_rate_to_base_currency_subbal6", StringType()),  # *
            StructField("cost_price_currency_code_subbal6", StringType()),  # *
            StructField("cost_price_amount_subbal6", StringType()),  # *
            StructField("not_realized_market_value_profit_currency_code_subbal6", StringType()),  # *
            StructField("not_realized_market_value_profit_amount_subbal6", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_currency_code_subbal6", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_amount_subbal6", StringType()),  # *
            StructField("place_of_safekeeping_subbal6", StringType()),  # *
            StructField("balance_qualifier_subbal7", StringType()),  # *
            StructField("balance_description_subbal7", StringType()),  # *
            StructField("balance_type_code_subbal7", StringType()),  # *
            StructField("balance_available_code_subbal7", StringType()),  # *
            StructField("balance_amount_subbal7", StringType()),  # *
            StructField("source_of_price_subbal7", StringType()),  # *
            StructField("place_of_safekeeping_code_subbal7", StringType()),  # *
            StructField("place_of_safekeeping_bicsubbal7", StringType()),  # *
            StructField("place_of_safekeeping_country_code_subbal7", StringType()),  # *
            StructField("market_price_type_code_subbal7", StringType()),  # *
            StructField("market_price_currency_code_subbal7", StringType()),  # *
            StructField("market_price_value_subbal7", StringType()),  # *
            StructField("price_quotation_date_subbal7", StringType()),  # *
            StructField("number_of_days_accrued_subbal7", StringType()),  # *
            StructField("holding_value_currency_code_subbal7", StringType()),  # *
            StructField("holding_value_amount_subbal7", StringType()),  # *
            StructField("accrued_interest_currency_code_subbal7", StringType()),  # *
            StructField("accrued_interest_amount_subbal7", StringType()),  # *
            StructField("book_value_currency_code_subbal7", StringType()),  # *
            StructField("book_value_amount_subbal7", StringType()),  # *
            StructField("exchange_rate_first_currency_code_subbal7", StringType()),  # *
            StructField("exchange_rate_second_currency_code_subbal7", StringType()),  # *
            StructField("exchange_rate_value_subbal7", StringType()),  # *
            StructField("security_currency_code_subbal7", StringType()),  # *
            StructField("security_currency_exchange_rate_to_base_currency_subbal7", StringType()),  # *
            StructField("cost_price_currency_code_subbal7", StringType()),  # *
            StructField("cost_price_amount_subbal7", StringType()),  # *
            StructField("not_realized_market_value_profit_currency_code_subbal7", StringType()),  # *
            StructField("not_realized_market_value_profit_amount_subbal7", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_currency_code_subbal7", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_amount_subbal7", StringType()),  # *
            StructField("place_of_safekeeping_subbal7", StringType()),  # *
            StructField("balance_qualifier_subbal8", StringType()),  # *
            StructField("balance_description_subbal8", StringType()),  # *
            StructField("balance_type_code_subbal8", StringType()),  # *
            StructField("balance_available_code_subbal8", StringType()),  # *
            StructField("balance_amount_subbal8", StringType()),  # *
            StructField("source_of_price_subbal8", StringType()),  # *
            StructField("place_of_safekeeping_code_subbal8", StringType()),  # *
            StructField("place_of_safekeeping_bicsubbal8", StringType()),  # *
            StructField("place_of_safekeeping_country_code_subbal8", StringType()),  # *
            StructField("market_price_type_code_subbal8", StringType()),  # *
            StructField("market_price_currency_code_subbal8", StringType()),  # *
            StructField("market_price_value_subbal8", StringType()),  # *
            StructField("price_quotation_date_subbal8", StringType()),  # *
            StructField("number_of_days_accrued_subbal8", StringType()),  # *
            StructField("holding_value_currency_code_subbal8", StringType()),  # *
            StructField("holding_value_amount_subbal8", StringType()),  # *
            StructField("accrued_interest_currency_code_subbal8", StringType()),  # *
            StructField("accrued_interest_amount_subbal8", StringType()),  # *
            StructField("book_value_currency_code_subbal8", StringType()),  # *
            StructField("book_value_amount_subbal8", StringType()),  # *
            StructField("exchange_rate_first_currency_code_subbal8", StringType()),  # *
            StructField("exchange_rate_second_currency_code_subbal8", StringType()),  # *
            StructField("exchange_rate_value_subbal8", StringType()),  # *
            StructField("security_currency_code_subbal8", StringType()),  # *
            StructField("security_currency_exchange_rate_to_base_currency_subbal8", StringType()),  # *
            StructField("cost_price_currency_code_subbal8", StringType()),  # *
            StructField("cost_price_amount_subbal8", StringType()),  # *
            StructField("not_realized_market_value_profit_currency_code_subbal8", StringType()),  # *
            StructField("not_realized_market_value_profit_amount_subbal8", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_currency_code_subbal8", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_amount_subbal8", StringType()),  # *
            StructField("place_of_safekeeping_subbal8", StringType()),  # *
            StructField("balance_qualifier_subbal9", StringType()),  # *
            StructField("balance_description_subbal9", StringType()),  # *
            StructField("balance_type_code_subbal9", StringType()),  # *
            StructField("balance_available_code_subbal9", StringType()),  # *
            StructField("balance_amount_subbal9", StringType()),  # *
            StructField("source_of_price_subbal9", StringType()),  # *
            StructField("place_of_safekeeping_code_subbal9", StringType()),  # *
            StructField("place_of_safekeeping_bicsubbal9", StringType()),  # *
            StructField("place_of_safekeeping_country_code_subbal9", StringType()),  # *
            StructField("market_price_type_code_subbal9", StringType()),  # *
            StructField("market_price_currency_code_subbal9", StringType()),  # *
            StructField("market_price_value_subbal9", StringType()),  # *
            StructField("price_quotation_date_subbal9", StringType()),  # *
            StructField("number_of_days_accrued_subbal9", StringType()),  # *
            StructField("holding_value_currency_code_subbal9", StringType()),  # *
            StructField("holding_value_amount_subbal9", StringType()),  # *
            StructField("accrued_interest_currency_code_subbal9", StringType()),  # *
            StructField("accrued_interest_amount_subbal9", StringType()),  # *
            StructField("book_value_currency_code_subbal9", StringType()),  # *
            StructField("book_value_amount_subbal9", StringType()),  # *
            StructField("exchange_rate_first_currency_code_subbal9", StringType()),  # *
            StructField("exchange_rate_second_currency_code_subbal9", StringType()),  # *
            StructField("exchange_rate_value_subbal9", StringType()),  # *
            StructField("security_currency_code_subbal9", StringType()),  # *
            StructField("security_currency_exchange_rate_to_base_currency_subbal9", StringType()),  # *
            StructField("cost_price_currency_code_subbal9", StringType()),  # *
            StructField("cost_price_amount_subbal9", StringType()),  # *
            StructField("not_realized_market_value_profit_currency_code_subbal9", StringType()),  # *
            StructField("not_realized_market_value_profit_amount_subbal9", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_currency_code_subbal9", StringType()),  # *
            StructField("not_realized_foreign_exchange_profit_amount_subbal9", StringType()),  # *
            StructField("place_of_safekeeping_subbal9", StringType()),  # *
            StructField("financ_instr_price_qualifier", StringType()),  # *
            StructField("financ_instr_price_percentage_type_code", StringType()),  # *
            StructField("financ_instr_price_in_percent", StringType()),  # *
            StructField("financ_instr_price_amount_type_code", StringType()),  # *
            StructField("financ_instr_price_currency_code", StringType()),  # *
            StructField("financ_instr_price", StringType()),  # *
            StructField("financ_instr_price_code", StringType()),  # *
            StructField("accrued_interest_currency_code_position", StringType()),
            StructField("accrued_interest_amount_position", StringType()),  # LongType()
        ]),
        "cash": StructType([
            StructField("transaction_reference_number", StringType()),
            StructField("related_reference_number", StringType()),  # *
            StructField("account_identification", StringType()),
            StructField("statement_number_sequence_number", StringType()),  # IntegerType()
            StructField("closing_balance_dealt_credit_debit_indicator", StringType()),
            StructField("closing_balance_value_date", DateType()),
            StructField("closing_balance_currency_code", StringType()),
            StructField("closing_balance_amount", DoubleType()),
            StructField("closing_available_bal_settld_credit_debit", StringType()),
            StructField("closing_available_bal_settld_value_date", DateType()),
            StructField("closing_available_bal_settld_currency_code", StringType()),
            StructField("closing_available_bal_settld_amount", DoubleType()),
            StructField("forward_available_balance", StringType()),  # DoubleType()
            StructField("interest_rate", DoubleType()),
            StructField("accrued_interest_negative_currency_code", StringType()),  # *
            StructField("accrued_interest_negative_amount", StringType()),  # *
            StructField("account_currency_code", StringType()),
            StructField("account_currency_exchange_rate_to_base_currency", DoubleType()),
            StructField("reference_currency_code", StringType()),
            StructField("reference_currency_exchange_rate_to_base_currency", DoubleType()),
            StructField("accrued_interest_amount_currency_code", StringType()),
            StructField("accrued_interest_amount", StringType()),  # DoubleType()
            StructField("withholding_tax_currency_code", StringType()),  # *
            StructField("withholding_tax_amount", StringType()),  # *
            StructField("fiduciary_call_deposit", StringType()),  # *
            StructField("fiduciary_call_term", StringType()),  # *
            StructField("money_market_call", StringType()),  # *
            StructField("money_market_term", StringType()),  # *
            StructField("redemption_date", DateType()),
            StructField("deposit_sequence_number", StringType()),
            StructField("business_deal_type", StringType()),
            StructField("objecttype_code", StringType()),
            StructField("parent_account_number", StringType()),  # LongType()
        ]),
        "transactions": StructType([
            StructField("senders_reference_number", StringType()),
            StructField("related_reference_number", StringType()),
            StructField("type_of_operation", StringType()),
            StructField("scope_of_operation", StringType()),  # *
            StructField("type_of_event", StringType()),
            StructField("bank_code1", StringType()),
            StructField("location_code1", StringType()),
            StructField("reference_code", StringType()),
            StructField("identifier_party_a", StringType()),
            StructField("identification_party_a", StringType()),  # *
            StructField("identifier_party_b", StringType()),
            StructField("brokers_commission_currency_code", StringType()),  # *
            StructField("brokers_commission_amount", StringType()),  # *
            StructField("loco_charge_account", StringType()),  # *
            StructField("value_added_tax_currency_code", StringType()),  # *
            StructField("value_added_tax_amount", StringType()),  # *
            StructField("vata_charge_account", StringType()),  # *
            StructField("cantonal_charges_currency_code", StringType()),  # *
            StructField("cantonal_charges_amount", StringType()),  # *
            StructField("locl_charge_account", StringType()),  # *
            StructField("cash_movement_booking_text", StringType()),  # *
            StructField("charge_account", StringType()),  # *
            StructField("eu_tax_retention_currency_code", StringType()),  # *
            StructField("eu_tax_retention_amount", StringType()),  # *
            StructField("eutr_charge_account", StringType()),  # *
            StructField("value_added_tax_on_commissions_currency_code", StringType()),  # *
            StructField("value_added_tax_on_commissions_amount", StringType()),  # *
            StructField("vatm_charge_account", StringType()),  # *
            StructField("role_of_party_a", StringType()),
            StructField("trade_date", DateType()),
            StructField("value_date", DateType()),
            StructField("period_of_notice", StringType()),  # IntegerType()
            StructField("balance_currency_code", StringType()),
            StructField("balance_amount", StringType()),  # DoubleType()
            StructField("amount_to_be_settled_currency_code", StringType()),  # *
            StructField("amount_to_be_settled", StringType()),  # *
            StructField("next_interest_due_date", StringType()),  # *
            StructField("interest_currency_code", StringType()),  # *
            StructField("interest_amount", StringType()),  # *
            StructField("interest_rate", DoubleType()),
            StructField("day_count_fraction_code", StringType()),
            StructField("receiving_party_identifier_seq_c", StringType()),
            StructField("receiving_party_identifier_seq_d", StringType()),
            StructField("receiving_party_identifier_seq_e", StringType()),
            StructField("tax_rate", StringType()),  # *
            StructField("transaction_currency", StringType()),  # *
            StructField("net_interest_amount", StringType()),  # *
            StructField("exchange_rate", StringType()),  # *
            StructField("reporting_currency", StringType()),  # *
            StructField("tax_amount", StringType()),  # *
            StructField("counterpartys_reference", StringType()),  # LongType()
            StructField("origin_of_income", StringType()),  # *
            StructField("deposit_number", StringType()),  # *
            StructField("type_of_deposit_indicator", StringType()),
            StructField("business_transaction_type", StringType()),
            StructField("parent_account_number", StringType()),
            StructField("deposit_account_name", StringType()),  # *
            StructField("deposit_currency_code_exchange_rate", StringType()),  # *
            StructField("deposit_currency_exchange_rate_to_base_currency", StringType()),  # *
            StructField("account_currency_code_exchange_rate", StringType()),
            StructField("account_currency_exchange_rate_to_base_currency", DoubleType()),
            StructField("reference_exchange_rate_currency_code", StringType()),
            StructField("reference_exchange_rate", DoubleType()),
            StructField("previous_interest_rate", StringType()),  # *
            StructField("redemption_date", DateType()),
            StructField("safekeeping_account", StringType()),
            StructField("deal_specialization_code", StringType()),
            StructField("settlement_information", StringType()),  # *
            StructField("transaction_specialization_code", StringType()),
            StructField("loan_or_mortgage", StringType()),  # *
            StructField("contract_account", StringType()),  # *
        ]),
    }

    return spark_schema_dict[table_tag]
