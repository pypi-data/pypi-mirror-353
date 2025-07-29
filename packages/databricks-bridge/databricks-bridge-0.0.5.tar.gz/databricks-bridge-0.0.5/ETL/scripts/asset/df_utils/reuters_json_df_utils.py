from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns

db_name = "cleansed"
data_source = "asset_reuters_json"


def get_data_lineage(table_name, file_tag):
    return {
        'target_type': "lakehouse",
        'target_endpoint': table_name,
        'src0_type': "s3",
        'src0_endpoint': f"landing/asset/public_listed/reuters/json/{file_tag.replace('_', '-')}",
        'etl_script_path': "ETL/scripts/asset/all_reuters_json.py",
        'src1_type': "service",
        'src1_endpoint': "ms-datalake-connector",
        'src1_script_path': "src/main/kotlin/com/ytree/msdatalakeconnector/adapter/driver/kafka/listener/AssetEventListener.kt",
        'src2_type': "kafka",
        'src2_endpoint': "MS_DATALAKE_CONNECTOR_ASSET_EVENT_TOPIC",
        'src2_script_path': ""
    }


class TablesDynamic(ABC):
    @abstractmethod
    def create_table(self):
        raise NotImplementedError

    @staticmethod
    def get_spark_schema():
        raise NotImplementedError

    @abstractmethod
    def delete_table(self):
        raise NotImplementedError


class CompositeTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "composite"
        self.table_name = f"{db_name}.{data_source}_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name, self.file_tag)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("file_id", StringType()),
            StructField("odata_context", StringType()),
            StructField("actively_managed_et_f_flag", StringType()), #*
            StructField("annual_management_charge", DoubleType()),
            StructField("beta_1_year", DoubleType()),
            StructField("beta_3_years", DoubleType()),
            StructField("beta_5_years", DoubleType()),
            StructField("beta_10_years", DoubleType()),
            StructField("bid_ask_spread", DoubleType()),
            StructField("currency_code", StringType()),
            StructField("fund_manager_benchmark", StringType()),
            StructField("fund_objective", StringType()),
            StructField("identifier", StringType()),
            StructField("identifier_type", StringType()),
            StructField("maximum_annual_management_charge", StringType()), #*
            StructField("maximum_redemption_charge", StringType()), #*
            StructField("minimum_annual_management_charge", StringType()), #*
            StructField("minimum_redemption_charge", StringType()), #*
            StructField("moodys_rating", StringType()), #*
            StructField("net_asset_value", DoubleType()), #*
            StructField("par_value", DoubleType()),
            StructField("redemption_charge", DoubleType()), #*
            StructField("total_return_index", DoubleType()),
            StructField("trading_status", IntegerType()),
            StructField("universal_close_price", DoubleType()),
            StructField("universal_close_price_date", DateType()),
            StructField("notes", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class FundAllocationTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "fund_allocation"
        self.table_name = f"{db_name}.{data_source}_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name, self.file_tag)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("file_id", StringType()),
            StructField("odata_context", StringType()),
            StructField("allocation_item", StringType()),
            StructField("allocation_percentage", DoubleType()),
            StructField("allocation_type", StringType()),
            StructField("identifier", StringType()),
            StructField("identifier_type", StringType()),
            StructField("notes", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class PriceHistoryTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "price_history"
        self.table_name = f"{db_name}.{data_source}_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name, self.file_tag)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("file_id", StringType()),
            StructField("odata_context", StringType()),
            StructField("currency_code", StringType()),
            StructField("identifier", StringType()),
            StructField("identifier_type", StringType()),
            StructField("trade_date", DateType()),
            StructField("universal_close_price", DoubleType()),
            StructField("notes", StringType()),
            StructField("error", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class TermAndConditionsTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "term_and_conditions"
        self.table_name = f"{db_name}.{data_source}_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name, self.file_tag)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("file_id", StringType()),
            StructField("odata_context", StringType()),
            StructField("analysis_benchmark_legal_name", StringType()),
            StructField("asset_type", StringType()),
            StructField("currency_code", StringType()),
            StructField("domicile", StringType()),
            StructField("fund_legal_structure", StringType()),
            StructField("identifier", StringType()),
            StructField("identifier_type", StringType()),
            StructField("initial_fund_charge", DoubleType()), #*
            StructField("isin", StringType()),
            StructField("lipper_global_classification", StringType()),
            StructField("maximum_initial_fund_charge", DoubleType()), #*
            StructField("minimum_initial_fund_charge", StringType()), #*
            StructField("moodys_rating", StringType()), #*
            StructField("par_value", DoubleType()),
            StructField("ric", StringType()),
            StructField("security_description", StringType()),
            StructField("security_long_name", StringType()),
            StructField("settlement_date_convention", StringType()),
            StructField("total_expense_ratio_value", StringType()),
            StructField("yield_value", DoubleType()), #*
            StructField("notes", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
