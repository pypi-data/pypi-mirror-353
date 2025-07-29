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


class RBCWealthTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "dd/MM/yyyy"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "val":
            self.table_tag = "holdings"
            self.date_format = {"*": "dd-MMM-yyyy"}
        elif file_tag == "trn":
            self.table_tag = "transactions"
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.rbc_wealth_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/rbc"
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
            StructField("cust_no", StringType()),
            StructField("cust_name", StringType()),
            StructField("port_no", StringType()),  # IntegerType()
            StructField("port_ccy", StringType()),
            StructField("item_ccy", StringType()),
            StructField("item_desc", StringType()),
            StructField("holding", DoubleType()),
            StructField("stock_cost", DoubleType()),
            StructField("book_cost", DoubleType()),
            StructField("stock_valu", DoubleType()),
            StructField("book_value", DoubleType()),
            StructField("stock_pl", DoubleType()),
            StructField("book_pl", DoubleType()),
            StructField("acc_int_sk", DoubleType()),
            StructField("valn_date", DateType()),
            StructField("sec_type", StringType()),
            StructField("last_price", DoubleType()),
            StructField("bk_acc_int", DoubleType()),
            StructField("isin", StringType()),
            StructField("rate", DoubleType()),
            StructField("sect_ticker_code", StringType()),
            StructField("reddate", StringType()),  # *
            StructField("id", StringType()),
            StructField("price_date", DateType()),
        ]),
        "transactions": StructType([
            StructField("customer_name", StringType()),
            StructField("customer_number", StringType()),
            StructField("portfolio_number", StringType()),  # IntegerType()
            StructField("account_number", StringType()),
            StructField("transaction_id", StringType()),
            StructField("reversed", StringType()),
            StructField("trade_date", DateType()),
            StructField("settlement_date", DateType()),
            StructField("posted_date", DateType()),
            StructField("transaction_type", StringType()),
            StructField("sedol", StringType()),
            StructField("isin", StringType()),
            StructField("security_name", StringType()),
            StructField("security_ccy", StringType()),
            StructField("quantity", DoubleType()),
            StructField("price_dividend_rate", DoubleType()),
            StructField("settlement_ccy", StringType()),
            StructField("exchange_rate", DoubleType()),
            StructField("settlement_amount", DoubleType()),
            StructField("settlement_account", StringType()),
            StructField("settlement_ccy_1", StringType()),  # *
            StructField("exchange_rate_1", DoubleType()),
            StructField("settlement_amount_1", DoubleType()),
            StructField("settlement_account_1", StringType()),  # *
            StructField("settlement_ccy_2", StringType()),  # *
            StructField("exchange_rate_2", DoubleType()),
            StructField("settlement_amount_2", DoubleType()),
            StructField("settlement_account_2", StringType()),  # *
            StructField("settlement_ccy_3", StringType()),  # *
            StructField("exchange_rate_3", DoubleType()),
            StructField("settlement_amount_3", DoubleType()),
            StructField("settlement_account_3", StringType()),  # *
            StructField("narrative1", StringType()),
            StructField("narrative2", StringType()),
            StructField("gross_amount_ccy", StringType()),
            StructField("gross_amount", DoubleType()),
            StructField("accrued_interest_ccy", StringType()),  # *
            StructField("accured_interest_amount", DoubleType()),
            StructField("brokerage_charge_ccy", StringType()),  # *
            StructField("brokerage_charge_amount", DoubleType()),
            StructField("csi_levy_ccy", StringType()),  # *
            StructField("csi_levy_amount", DoubleType()),
            StructField("stamp_duty_ccy", StringType()),  # *
            StructField("stamp_duty_amount", DoubleType()),
            StructField("taxes_and_other_charges_ccy", StringType()),  # *
            StructField("taxes_and_other_charges_amount", DoubleType()),
            StructField("tax_credit_ccy", StringType()),
            StructField("tax_credit_amount", DoubleType()),
            StructField("price_adjustment_ccy", StringType()),  # *
            StructField("tax_adjustment_amount", DoubleType()),
            StructField("courier_charge_ccy", StringType()),  # *
            StructField("courier_charge_amount", DoubleType()),
            StructField("rbc_transaction_fee_ccy", StringType()),  # *
            StructField("rbc_transaction_fee_amount", DoubleType()),
            StructField("im_charge_ccy", StringType()),  # *
            StructField("im_charge_amount", DoubleType()),
            StructField("eusd_retention_tax_ccy", StringType()),  # *
            StructField("eusd_retention_tax_amount", DoubleType()),
            StructField("withholding_tax_ccy", StringType()),
            StructField("withholding_tax_amount", DoubleType()),
            StructField("withholding_tax_adjustment_ccy", StringType()),  # *
            StructField("withholding_tax_adjustment_amount", DoubleType()),
            StructField("refund_ccy", StringType()),  # *
            StructField("refund_amount", DoubleType()),
            StructField("payment_charge_ccy", StringType()),  # *
            StructField("payment_charge_amount", DoubleType()),
            StructField("dividend_additional_charge_ccy", StringType()),  # *
            StructField("dividend_additional_charge_amount", DoubleType()),
            StructField("dividend_adjustment_ccy", StringType()),  # *
            StructField("dividend_adjustment_amount", DoubleType()),
            StructField("net_amount_ccy", StringType()),  # *
            StructField("net_amount", DoubleType()),
            StructField("misc1", StringType()),  # *
            StructField("misc2", DoubleType()),
            StructField("misc3", StringType()),  # *
            StructField("misc4", DoubleType()),
            StructField("misc5", StringType()),  # *
            StructField("misc6", DoubleType()),
            StructField("misc7", StringType()),  # *
            StructField("misc8", DoubleType()),
            StructField("misc9", StringType()),  # *
            StructField("misc10", DoubleType()),
            StructField("misc11", StringType()),  # *
            StructField("misc12", DoubleType()),
            StructField("misc13", StringType()),  # *
            StructField("misc14", DoubleType()),
            StructField("misc15", StringType()),  # *
            StructField("misc16", DoubleType()),
            StructField("misc17", StringType()),  # *
            StructField("misc18", DoubleType()),
            StructField("misc19", StringType()),  # *
            StructField("misc20", DoubleType()),
            StructField("misc21", StringType()),  # *
            StructField("misc22", DoubleType()),
            StructField("misc23", StringType()),  # *
            StructField("misc24", DoubleType()),
            StructField("misc25", StringType()),  # *
            StructField("misc26", DoubleType()),
            StructField("misc27", StringType()),  # *
            StructField("misc28", DoubleType()),
            StructField("misc29", StringType()),  # *
            StructField("misc30", DoubleType()),
            StructField("misc31", StringType()),  # *
            StructField("misc32", DoubleType()),
            StructField("dividend_xd_date", DateType()),
            StructField("transaction_ref", StringType()),
        ]),
    }

    return spark_schema_dict[table_tag]
