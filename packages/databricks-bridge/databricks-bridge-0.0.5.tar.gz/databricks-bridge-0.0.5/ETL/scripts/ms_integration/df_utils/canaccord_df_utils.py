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


class CanaccordTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = "\t"
        self.file_tag = file_tag
        self.date_format = {"*": "dd/MM/yyyy"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "val":
            self.table_tag = "holdings"
            self.column_line = [self.sep.join(["Statement_Date", "Asset_Type", "col_3", "Account_Currency", "Account_number_1", "Account_number_2", "Account_number_3", "Asset_ID", "Asset_Currency", "Asset_Name", "Asset_Type_1", "Domicile", "Quantity", "Price", "Value_held"])]
        elif file_tag == "cash_activity":
            self.table_tag = "transactions"
        elif file_tag == "contracts":
            self.table_tag = file_tag
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.canaccord_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/canaccord"
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
            StructField("statement_date", DateType()),
            StructField("asset_type", StringType()),
            StructField("col3", StringType()),  # *
            StructField("account_currency", StringType()),
            StructField("account_number1", StringType()),
            StructField("account_number2", StringType()),
            StructField("account_number3", StringType()),
            StructField("asset_id", StringType()),
            StructField("asset_currency", StringType()),
            StructField("asset_name", StringType()),
            StructField("asset_type1", StringType()),
            StructField("domicile", StringType()),
            StructField("quantity", DoubleType()),
            StructField("price", DoubleType()),
            StructField("value_held", DoubleType()),
        ]),
        "transactions": StructType([
            StructField("account", StringType()),
            StructField("ccy", StringType()),
            StructField("clientcode", StringType()),
            StructField("containernr", DoubleType()),
            StructField("name", StringType()),
            StructField("short_name", StringType()),
            StructField("trade_date", DateType()),
            StructField("value_date", DateType()),
            StructField("isin", StringType()),
            StructField("bargain", StringType()),
            StructField("contra", StringType()),
            StructField("quantity", DoubleType()),
            StructField("type", StringType()),
            StructField("amount", DoubleType()),
            StructField("description", StringType()),
        ]),
        "contracts": StructType([
            StructField("bargain_date", DateType()),
            StructField("settlement_date", DateType()),
            StructField("isin", StringType()),
            StructField("client_code", StringType()),
            StructField("container_nr", DoubleType()),
            StructField("name1", StringType()),
            StructField("bargain", StringType()),
            StructField("contra", StringType()),
            StructField("contra_bargain", StringType()),
            StructField("purchase_sale", StringType()),
            StructField("stock_issuer", StringType()),
            StructField("stock_name", StringType()),
            StructField("message1", StringType()),
            StructField("message2", StringType()),
            StructField("net", StringType()),
            StructField("contract_time", StringType()),
            StructField("quantity", DoubleType()),
            StructField("price", DoubleType()),
            StructField("market_ccy", StringType()),
            StructField("consideration", DoubleType()),
            StructField("accrued_days", StringType()),
            StructField("accrued_rate", StringType()),
            StructField("accrued_interest", DoubleType()),
            StructField("x_rate", DoubleType()),
            StructField("settlement_ccy", StringType()),
            StructField("settlement_total", DoubleType()),
            StructField("expenses_ccy", StringType()),
            StructField("commission", DoubleType()),
            StructField("ptm", StringType()),
            StructField("special", DoubleType()),
            StructField("stamp", DoubleType()),
            StructField("contract_total", DoubleType()),
            StructField("rate1", DoubleType()),
            StructField("rate2", DoubleType()),
            StructField("rate3", DoubleType()),
            StructField("fa_charge", DoubleType()),
            StructField("order_type", StringType()),
            StructField("venue", StringType()),
            StructField("special_text1", StringType()),
            StructField("special1", StringType()),
            StructField("special_text2", StringType()),
            StructField("special2", StringType()),
            StructField("special_text3", StringType()),
            StructField("special3", StringType()),
        ])
    }

    return spark_schema_dict[table_tag]
