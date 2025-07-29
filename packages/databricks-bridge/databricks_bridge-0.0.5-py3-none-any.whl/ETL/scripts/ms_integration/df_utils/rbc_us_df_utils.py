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


class RBCUSTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "yyyyMMdd"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "po":
            self.table_tag = "positions"
        elif file_tag == "tr":
            self.table_tag = "transactions"
        elif file_tag == "tf":
            self.table_tag = "trades"
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.rbc_us_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/rbc_us"
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
            StructField("firm_branch_fa", StringType()),
            StructField("account_number", StringType()),  # LongType()
            StructField("balance_type", StringType()),
            StructField("security_number", StringType()),
            StructField("trade_date_quantity", DoubleType()),
            StructField("trade_date_value", DoubleType()),
            StructField("cusip", StringType()),
            StructField("symbol", StringType()),
            StructField("security_type", StringType()),
            StructField("security_sub_types", StringType()),  # *
            StructField("position_date", DateType()),
            StructField("option_type", StringType()),  # *
            StructField("account_code", StringType()),
            StructField("account_type", StringType()),  # IntegerType()
            StructField("marginable_code", StringType()),  # IntegerType()
            StructField("factor", DoubleType()),
            StructField("other_balance_on_trade_date", DoubleType()),
            StructField("asset_type", StringType()),  # *
            StructField("rbc_security_number", StringType()),  # LongType()
            StructField("occ_symbol", StringType()),  # *
            StructField("opra_symbol", StringType()),  # *
            StructField("thomson_one_symbol", StringType()),  # *
            StructField("expanded_symbol", StringType()),
            StructField("dollarised_trade_date_amount", StringType()),  # IntegerType()
            StructField("settlement_date_balance", DoubleType()),
            StructField("settlement_date_quantity", DoubleType()),
            StructField("estimated_settlement_date_value", DoubleType()),
            StructField("market_price", DoubleType()),
            StructField("account_iso_code", StringType()),
            StructField("account_currency_symbol_code", StringType()),
            StructField("account_numeric_currency_code", StringType()),
            StructField("security_iso_code", StringType()),
            StructField("security_currency_symbol", StringType()),
            StructField("security_numeric_currency_code", StringType()),
            StructField("exchange_rate", DoubleType()),
            StructField("sedol", StringType()),
            StructField("isin", StringType()),
            StructField("alt_branch", StringType()),
            StructField("financial_adviser", StringType()),
            StructField("short_name", StringType()),
            StructField("desc_line_1", StringType()),
            StructField("desc_line_2", StringType()),
            StructField("desc_line_3", StringType()),  # *
        ]),
        "transactions": StructType([
            StructField("firm_branch_fa", StringType()),
            StructField("category_code", StringType()),
            StructField("record_code", StringType()),
            StructField("date", DateType()),
            StructField("account_number", StringType()),  # LongType()
            StructField("account_type", StringType()),  # IntegerType()
            StructField("quantity", DoubleType()),
            StructField("net_amount_of_transaction", DoubleType()),
            StructField("date_posted", DateType()),
            StructField("as_of_date", DateType()),
            StructField("security_number", StringType()),
            StructField("description_line_1", StringType()),
            StructField("description_line_2", StringType()),
            StructField("cusip", StringType()),
            StructField("symbol", StringType()),
            StructField("account_code", StringType()),
            StructField("value_of_transaction", DoubleType()),
            StructField("batch_code", StringType()),
            StructField("entry_code", StringType()),
            StructField("rbc_security_number", StringType()),  # LongType()
            StructField("occ_symbol", StringType()),  # *
            StructField("opra_symbol", StringType()),  # *
            StructField("thomson_one_symbol", StringType()),  # *
            StructField("expanded_symbol", StringType()),
            StructField("account_iso_code", StringType()),
            StructField("account_currency_symbol", StringType()),
            StructField("account_numeric_currency_code", StringType()),
            StructField("security_iso_code", StringType()),
            StructField("security_currency_symbol", StringType()),
            StructField("security_numeric_currency_code", StringType()),
            StructField("exchange_rate", DoubleType()),
            StructField("sedol", StringType()),
            StructField("isin", StringType()),
            StructField("description_line_3", StringType()),
            StructField("description_line_4", StringType()),
            StructField("description_line_5", StringType()),
            StructField("description_line_6", StringType()),
            StructField("description_line_7", StringType()),  # *
        ]),
        "trades": StructType([
            StructField("firm_branch_fa", StringType()),
            StructField("marginable", StringType()),  # IntegerType()
            StructField("security_type", StringType()),
            StructField("account_number", StringType()),  # LongType()
            StructField("account_type", StringType()),  # IntegerType()
            StructField("bond_basis_yield", DoubleType()),
            StructField("trade_date", DateType()),
            StructField("settlement_date", DateType()),
            StructField("as_of_date", StringType()),  # DateType
            StructField("security_number", StringType()),
            StructField("quantity", DoubleType()),
            StructField("price", DoubleType()),
            StructField("buy_or_sell", StringType()),
            StructField("cancel_rebill_indicator", StringType()),  # *
            StructField("blotter_code", StringType()),  # IntegerType()
            StructField("discretion_exercised", StringType()),  # *
            StructField("accrued_date", StringType()),  # DateType()
            StructField("tto_rep_id", StringType()),  # *
            StructField("principal", DoubleType()),
            StructField("sec_fee", DoubleType()),
            StructField("commission", DoubleType()),
            StructField("net_amount", DoubleType()),
            StructField("no_postage_indicator", StringType()),
            StructField("symbol", StringType()),
            StructField("special_tax_indicator", StringType()),  # *
            StructField("offset_entity", StringType()),  # *
            StructField("offset_entity_type", StringType()),  # *
            StructField("cusip", StringType()),
            StructField("underlying_security", StringType()),  # *
            StructField("strike_price", DoubleType()),
            StructField("discount", DoubleType()),
            StructField("commission_code", StringType()),  # *
            StructField("handling_fee", DoubleType()),
            StructField("basis_price", DoubleType()),
            StructField("factor", DoubleType()),
            StructField("muni_cb", StringType()),  # *
            StructField("security_subtype", StringType()),  # *
            StructField("sales_credit_code", StringType()),  # *
            StructField("nasdaq", StringType()),  # *
            StructField("security_description_1", StringType()),
            StructField("security_description_2", StringType()),
            StructField("security_description_3", StringType()),  # *
            StructField("security_description_4", StringType()),  # *
            StructField("security_description_5", StringType()),  # *
            StructField("security_description_6", StringType()),  # *
            StructField("order_number", StringType()),  # *
            StructField("prospectus_required", StringType()),  # *
            StructField("no_new_mexico_tax", StringType()),  # *
            StructField("filler1", StringType()),  # *
            StructField("full_commission", DoubleType()),
            StructField("execution_time", StringType()),
            StructField("filler2", StringType()),  # *
            StructField("filler3", StringType()),  # *
            StructField("market_price", DoubleType()),
            StructField("sales_credit_percentage", DoubleType()),
            StructField("postage_fees", DoubleType()),
            StructField("filler4", DoubleType()),
            StructField("otc_mm_flag", StringType()),  # *
            StructField("filler5", StringType()),  # *
            StructField("filler6", StringType()),  # *
            StructField("filler7", StringType()),  # *
            StructField("filler8", StringType()),  # *
            StructField("filler9", StringType()),  # *
            StructField("filler10", StringType()),  # *
            StructField("accrued_interest", DoubleType()),
            StructField("filler11", StringType()),  # *
            StructField("filler12", StringType()),  # *
            StructField("sales_credit_amount", DoubleType()),
            StructField("moodys", StringType()),  # *
            StructField("s_and_p", StringType()),  # *
            StructField("account_codes", StringType()),
            StructField("buy_instructions", StringType()),
            StructField("sell_instructions", StringType()),
            StructField("residence_state", StringType()),  # *
            StructField("foreign_tax_code", StringType()),  # *
            StructField("managed_code", StringType()),
            StructField("filler13", StringType()),  # *
            StructField("managed_account_advisor", StringType()),  # *
            StructField("account_class_code", StringType()),  # *
            StructField("option_level_code", StringType()),  # *
            StructField("special_commission_code", StringType()),
            StructField("discretionary_account_flag", StringType()),
            StructField("credit_interest", StringType()),  # *
            StructField("filler14", StringType()),  # *
            StructField("filler15", StringType()),  # *
            StructField("filler16", StringType()),  # IntegerType()
            StructField("cma", StringType()),  # *
            StructField("erisa", StringType()),  # *
            StructField("option_type", StringType()),  # *
            StructField("record_code", StringType()),
            StructField("seller_code", StringType()),  # *
            StructField("trailer_code_1", StringType()),
            StructField("trailer_code_2", StringType()),
            StructField("trailer_code_3", StringType()),  # *
            StructField("control_number", StringType()),
            StructField("mutual_fund_share_class", StringType()),  # *
            StructField("filler17", StringType()),  # *
            StructField("filler18", StringType()),  # *
            StructField("filler19", StringType()),  # *
            StructField("filler20", StringType()),  # *
            StructField("filler21", StringType()),  # *
            StructField("filler22", StringType()),  # *
            StructField("filler23", StringType()),  # *
            StructField("filler24", StringType()),  # *
            StructField("filler25", StringType()),  # *
            StructField("rbc_security_number", StringType()),  # LongType()
            StructField("trailer_code_4", StringType()),  # *
            StructField("trailer_code_5", StringType()),  # *
            StructField("trailer_code_6", StringType()),  # *
            StructField("trailer_code_7", StringType()),  # *
            StructField("trailer_code_8", StringType()),  # *
            StructField("trailer_code_9", StringType()),  # *
            StructField("trailer_code_10", StringType()),  # *
            StructField("occ_symbol", StringType()),  # *
            StructField("opra_symbol", StringType()),  # *
            StructField("thomson_one_symbol", StringType()),  # *
            StructField("expanded_symbol", StringType()),
            StructField("primary_exchange", StringType()),
            StructField("contra_mpid", StringType()),
            StructField("account_iso_code", StringType()),
            StructField("account_currency_symbol_code", StringType()),
            StructField("account_numeric_currency_code", StringType()),
            StructField("security_iso_code", StringType()),
            StructField("security_currency_symbol", StringType()),
            StructField("security_numeric_currency_code", StringType()),
            StructField("exchange_rate", DoubleType()),
            StructField("sedol", StringType()),
            StructField("isin", StringType()),
        ]),
    }

    return spark_schema_dict[table_tag]
