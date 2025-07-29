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


class BrooksMcdonaldTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "yyyyMMdd"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "":
            self.table_tag = "holdings"
        elif file_tag == "transactions":
            self.table_tag = file_tag
        elif file_tag == "tran":
            self.table_tag = file_tag
            self.date_format = {"*": "dd-MM-yyyy"}
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.brooks_mcdonald_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/brooks_mcdonald"
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
            StructField("client_ref_from_bmd", StringType()),
            StructField("policy_number_from_provider", StringType()),
            StructField("full_asset_name", StringType()),
            StructField("isin", StringType()),
            StructField("description_of_holding", StringType()),
            StructField("native_currency", StringType()),
            StructField("market", StringType()),
            StructField("nominal_units_held", DoubleType()),
            StructField("market_price", DoubleType()),
            StructField("quarter_up_price", DoubleType()),
            StructField("date_of_price_used", DateType()),
            StructField("market_value", DoubleType()),
            StructField("market_price_in_valuation_currency", DoubleType()),
            StructField("client_title", StringType()),
            StructField("forename", StringType()),
            StructField("surname", StringType()),
            StructField("date_of_birth", StringType()),
            StructField("national_insurance_number", StringType()),
            StructField("cash_value", DoubleType()),
            StructField("cash_value_in_base", DoubleType()),
            StructField("asset_manager", StringType()),
            StructField("asset_country", StringType()),
            StructField("value_in_acc_currency", DoubleType()),
            StructField("account_currency", StringType()),
            StructField("exchange_rate", DoubleType()),
            StructField("cash_currency", StringType()),
            StructField("additional_notes", StringType()),
            StructField("product_code", StringType()),
        ]),
        "transactions": StructType([
            StructField("transaction_date", DateType()),
            StructField("account_number", StringType()),
            StructField("transaction_type", StringType()),
            StructField("transaction_amount", DoubleType()),
            StructField("debit_credit", StringType()),
            StructField("transaction_currency", StringType()),
            StructField("transaction_description", StringType()),
        ]),
        "tran": StructType([
            StructField("account_no", StringType()),
            StructField("account_currency", StringType()),
            StructField("security_name", StringType()),
            StructField("security_currency", StringType()),
            StructField("sedol", StringType()),
            StructField("isin", StringType()),
            StructField("buysell", StringType()),
            StructField("transactioncode", StringType()),
            StructField("transaction_desc", StringType()),
            StructField("units", DoubleType()),
            StructField("market_price", DoubleType()),
            StructField("market_curr", StringType()),
            StructField("consideration", DoubleType()),
            StructField("consideration_curr", StringType()),
            StructField("transaction_date", DateType()),
            StructField("settlement_date", DateType()),
            StructField("settlement_trade_fx", StringType()),
            StructField("book_cost_acc_curr", StringType()),
            StructField("transaction_id", StringType()),
        ])
    }

    return spark_schema_dict[table_tag]
