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


class KillikTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "yyyyMMdd"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "holdings":
            self.table_tag = file_tag
            self.column_line = [self.sep.join([
                "Product_Code", "Security_CompanyName", "Security_Description", "Security_Ticker", "Security_Cusip",
                "Security_Isin", "Security_SEDOL", "Security_Type", "Security_Currency", "Security_Price",
                "Security_Exchange", "Security_TimeZone", "Quantity", "MarketValue", "MarketValue_GBP", "ShortLong",
                "Client id", "Product Type"])]
        elif file_tag == "transactions":
            self.table_tag = file_tag
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.killik_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/killik"
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
            StructField("product_code", StringType()),
            StructField("security_company_name", StringType()),
            StructField("security_description", StringType()),
            StructField("security_ticker", StringType()),
            StructField("security_cusip", StringType()),  # IntegerType()
            StructField("security_isin", StringType()),
            StructField("security_sedol", StringType()),
            StructField("security_type", StringType()),
            StructField("security_currency", StringType()),
            StructField("security_price", DoubleType()),
            StructField("security_exchange", StringType()),
            StructField("security_time_zone", StringType()),  # *
            StructField("quantity", StringType()),
            StructField("market_value", StringType()),  # DoubleType()
            StructField("market_value_gbp", StringType()),  # DoubleType()
            StructField("short_long", StringType()),
            StructField("client_id", StringType()),
            StructField("product_type", StringType()),
        ]),
        "transactions": StructType([
            StructField("killik_ref", StringType()),
            StructField("deleted", StringType()),  # IntegerType()
            StructField("product_code", StringType()),
            StructField("security_company_name", StringType()),
            StructField("security_description", StringType()),
            StructField("security_ticker", StringType()),
            StructField("security_cusip", StringType()),  # IntegerType()
            StructField("security_isin", StringType()),
            StructField("security_sedol", StringType()),
            StructField("security_type", StringType()),
            StructField("security_exchange", StringType()),
            StructField("security_time_zone", StringType()),  # *
            StructField("external_ref", StringType()),
            StructField("quantity", StringType()),  # *
            StructField("posted_amount", DoubleType()),
            StructField("currency_code", StringType()),
            StructField("ledger_type_name", StringType()),
            StructField("register_type_code", StringType()),
            StructField("is_dividend", StringType()),  # IntegerType()
            StructField("ledger_state_name", StringType()),
            StructField("ledger_category", StringType()),
            StructField("cancelled_ref", StringType()),  # *
            StructField("transaction_date", DateType()),
            StructField("transaction_time", StringType()),
            StructField("is_settled", StringType()),  # IntegerType()
            StructField("unit_price", StringType()),  # *
            StructField("unit_price_currency", StringType()),  # *
            StructField("original_cost", StringType()),  # *
            StructField("original_cost_currency", StringType()),  # *
            StructField("narrative1", StringType()),
            StructField("narrative2", StringType()),
            StructField("narrative3", StringType()),
            StructField("narrative4", StringType()),
            StructField("client_id", StringType()),
            StructField("product_type", StringType()),
        ]),
    }

    return spark_schema_dict[table_tag]
