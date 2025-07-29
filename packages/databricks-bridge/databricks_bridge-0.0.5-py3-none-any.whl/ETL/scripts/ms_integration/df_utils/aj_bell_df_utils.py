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


class AJBellTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.file_tag = file_tag
        self.unappendable_parent_keys = ["advisers", "clients", "products", "transactions", "valuations"]

        if file_tag == "valuations":
            self.table_tag = file_tag
        elif file_tag == "transactions":
            self.table_tag = file_tag
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.aj_bell_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/aj_bell"
        etl_path = "ETL/scripts/ms_integration/all_ms_integration_json.py"
        self.data_lineage = get_data_lineage(self.table_name, s3_endpoint, etl_path)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    def get_spark_schema(self):
        return non_essentialize_all_other_columns(get_table_schema(self.table_tag))

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


def get_table_schema(table_tag: str) -> StructType:
    spark_schema_dict = {
        "valuations": StructType([
            StructField("adviser_reference", StringType()),
            StructField("adviser_name", StringType()),
            StructField("client_reference", StringType()),
            StructField("client_first_names", StringType()),
            StructField("client_surname", StringType()),
            StructField("client_national_insurance_number", StringType()),
            StructField("product_name", StringType()),
            StructField("asset_source", StringType()),
            StructField("sedol", StringType()),
            StructField("isin", StringType()),
            StructField("asset_name", StringType()),
            StructField("units", DoubleType()),
            StructField("price", DoubleType()),
            StructField("value", DoubleType()),
            StructField("valuation_date", TimestampType()),
            StructField("currency", StringType()),
            StructField("book_cost", DoubleType()),
        ]),
        "transactions": StructType([
            StructField("adviser_reference", StringType()),
            StructField("adviser_name", StringType()),
            StructField("client_reference", StringType()),
            StructField("client_first_names", StringType()),
            StructField("client_surname", StringType()),
            StructField("client_national_insurance_number", StringType()),
            StructField("product_name", StringType()),
            StructField("transaction_source", StringType()),
            StructField("transaction_date_time", TimestampType()),
            StructField("effective_date", TimestampType()),
            StructField("settlement_date", TimestampType()),
            StructField("transaction_description", StringType()),
            StructField("asset_name", StringType()),
            StructField("sedol", StringType()),
            StructField("isin", StringType()),
            StructField("amount", DoubleType()),
            StructField("quantity", DoubleType()),
            StructField("dealing_charge", DoubleType()),
            StructField("stamp_duty", DoubleType()),
            StructField("reference", StringType()),
            StructField("venue", StringType()),
            StructField("currency", StringType()),
            StructField("currency_amount", DoubleType()),
            StructField("book_cost", DoubleType()),
        ])
    }

    return spark_schema_dict[table_tag]
