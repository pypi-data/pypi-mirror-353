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


class InteractiveBrokersTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "yyyy-MM-dd"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "activity":
            self.table_tag = file_tag
        elif file_tag == "account":
            self.table_tag = file_tag
        elif file_tag == "position":
            self.table_tag = file_tag
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.interactive_brokers_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/interactive_brokers"
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
        "activity": StructType([
            StructField("type", StringType()),  # *
            StructField("account_id", StringType()),  # *
            StructField("con_id", StringType()),  # *
            StructField("security_id", StringType()),  # *
            StructField("symbol", StringType()),  # *
            StructField("bb_ticker", StringType()),  # *
            StructField("bb_global_id", StringType()),  # *
            StructField("security_description", StringType()),  # *
            StructField("asset_type", StringType()),  # *
            StructField("currency", StringType()),  # *
            StructField("base_currency", StringType()),  # *
            StructField("trade_date", StringType()),  # *
            StructField("trade_time", StringType()),  # *
            StructField("settle_date", StringType()),  # *
            StructField("order_time", StringType()),  # *
            StructField("transaction_type", StringType()),  # *
            StructField("quantity", StringType()),  # *
            StructField("unit_price", StringType()),  # *
            StructField("gross_amount", StringType()),  # *
            StructField("sec_fee", StringType()),  # *
            StructField("commission", StringType()),  # *
            StructField("tax", StringType()),  # *
            StructField("net", StringType()),  # *
            StructField("net_in_base", StringType()),  # *
            StructField("trade_id", StringType()),  # *
            StructField("tax_basis_election", StringType()),  # *
            StructField("description", StringType()),  # *
            StructField("fx_rate_to_base", StringType()),  # *
            StructField("contra_party_name", StringType()),  # *
            StructField("clr_firm_id", StringType()),  # *
            StructField("exchange", StringType()),  # *
            StructField("master_account_id", StringType()),  # *
            StructField("van", StringType()),  # *
            StructField("away_broker_commission", StringType()),  # *
            StructField("order_id", StringType()),  # *
            StructField("client_reference", StringType()),  # *
            StructField("transaction_id", StringType()),  # *
            StructField("execution_id", StringType()),  # *
            StructField("cost_basis", StringType()),  # *
            StructField("flag", StringType()),  # *
            # StructField("", StringType()),
        ]),
        "account": StructType([
            StructField("type", StringType()),
            StructField("account_id", StringType()),
            StructField("account_title", StringType()),
            StructField("street", StringType()),
            StructField("street2", StringType()),
            StructField("city", StringType()),
            StructField("state", StringType()),
            StructField("zip", StringType()),
            StructField("country", StringType()),
            StructField("account_type", StringType()),
            StructField("customer_type", StringType()),
            StructField("base_currency", StringType()),
            StructField("master_account_id", StringType()),  # *
            StructField("van", StringType()),  # *
            StructField("capabilities", StringType()),
            StructField("alias", StringType()),  # *
            StructField("primary_email", StringType()),
            StructField("date_opened", DateType()),
            StructField("date_closed", StringType()),  # *
            StructField("date_funded", DateType()),
            StructField("account_representative", StringType()),
            # StructField("", StringType()),
        ]),
        "position": StructType([
            StructField("type", StringType()),
            StructField("account_id", StringType()),
            StructField("con_id", StringType()),  # *
            StructField("security_id", StringType()),  # *
            StructField("symbol", StringType()),  # *
            StructField("bb_ticker", StringType()),  # *
            StructField("bb_global_id", StringType()),  # *
            StructField("security_description", StringType()),  # *
            StructField("asset_type", StringType()),
            StructField("currency", StringType()),
            StructField("base_currency", StringType()),
            StructField("quantity", StringType()),  # LongType()
            StructField("quantity_in_base", StringType()),  # LongType()
            StructField("cost_price", StringType()),  # DoubleType()
            StructField("cost_basis", StringType()),  # DoubleType()
            StructField("cost_basis_in_base", StringType()),  # DoubleType()
            StructField("market_price", StringType()),  # DoubleType()
            StructField("market_value", StringType()),  # DoubleType()
            StructField("market_value_in_base", StringType()),  # DoubleType()
            StructField("open_date_time", StringType()),  # *
            StructField("fx_rate_to_base", StringType()),  # IntegerType()
            StructField("report_date", DateType()),
            StructField("settled_quantity", StringType()),  # LongType()
            StructField("settled_quantity_in_base", StringType()),  # LongType()
            StructField("master_account_id", StringType()),  # *
            StructField("van", StringType()),  # *
            StructField("accrued_int", StringType()),  # IntegerType()
            StructField("originating_order_id", StringType()),  # *
            StructField("multiplier", StringType()),  # IntegerType()
            # StructField("", StringType()),
        ]),
    }

    return spark_schema_dict[table_tag]
