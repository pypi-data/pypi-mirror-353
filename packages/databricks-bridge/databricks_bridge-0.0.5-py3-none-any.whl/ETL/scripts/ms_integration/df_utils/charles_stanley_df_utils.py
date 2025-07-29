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


class CharlesStanleyTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "dd/MM/yyyy"}
        self.column_line_index = 1
        self.column_line = []

        if file_tag == "cash":
            self.table_tag = file_tag
        elif file_tag == "transaction":
            self.table_tag = "transactions"
        elif file_tag == "holdings":
            self.table_tag = file_tag
        elif file_tag == "balance":
            self.table_tag = file_tag
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.charles_stanley_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/charles_stanley"
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
        "cash": StructType([
            StructField("h", StringType()),
            StructField("transaction_ref", StringType()),
            StructField("transaction_type", StringType()),
            StructField("client_account_ref", StringType()),
            StructField("sl_policy_no", StringType()),  # *
            StructField("transaction_date", DateType()),
            StructField("sedol", StringType()),
            StructField("stock_name", StringType()),  # *
            StructField("narrative", StringType()),
            StructField("currency", StringType()),  # *
            StructField("debit_amount", DoubleType()),
            StructField("credit_amount", DoubleType()),
            StructField("bank_account_no", StringType()),  # *
            StructField("tax_deducted", StringType()),  # *
            StructField("reversal", StringType()),  # *
        ]),
        "transactions": StructType([
            StructField("h", StringType()),
            StructField("bargain_ref", StringType()),  # *
            StructField("client_account_ref", StringType()),  # *
            StructField("sl_policy_no", StringType()),  # *
            StructField("transaction_type", StringType()),  # *
            StructField("bank_account_no", StringType()),  # *
            StructField("bargain_date", StringType()),  # *
            StructField("sedol", StringType()),  # *
            StructField("stock_name", StringType()),  # *
            StructField("quantity", StringType()),  # *
            StructField("currency", StringType()),  # *
            StructField("price", StringType()),  # *
            StructField("consideration", StringType()),
            StructField("accrued_interest", StringType()),
            StructField("stamp_duty", StringType()),
            StructField("ptm_levy", StringType()),
            StructField("other_charges", StringType()),
            StructField("commission", StringType()),
            StructField("total", StringType()),
            StructField("reversal", StringType()),  # *
            StructField("transaction_code", StringType()),  # *
            StructField("native_consideration", StringType()),  # *
            StructField("exchange_rate", StringType()),  # *
            StructField("trade_time", StringType()),  # *
            StructField("settlement_date", StringType()),  # *
            StructField("days_interest_acc", StringType()),  # *
            StructField("contract_note_price", StringType()),
            StructField("extra_description", StringType()),  # *
            StructField("client_settlement_currency", StringType()),  # *
            StructField("isin", StringType()),  # *
            StructField("order_type", StringType()),  # *
            StructField("venue", StringType()),  # *
        ]),
        "holdings": StructType([
            StructField("h", StringType()),
            StructField("client_account_ref", StringType()),
            StructField("sl_policy_no", StringType()),  # *
            StructField("sedol", StringType()),
            StructField("stock_name", StringType()),
            StructField("quantity", DoubleType()),
            StructField("currency", StringType()),
            StructField("price", DoubleType()),
        ]),
        "balance": StructType([
            StructField("h", StringType()),
            StructField("client_account_ref", StringType()),
            StructField("sl_policy_no", StringType()),  # *
            StructField("bank_account_no", StringType()),
            StructField("currency", StringType()),  # *
            StructField("account_balance", DoubleType()),
            StructField("service_level", StringType()),
        ]),
    }

    return spark_schema_dict[table_tag]
