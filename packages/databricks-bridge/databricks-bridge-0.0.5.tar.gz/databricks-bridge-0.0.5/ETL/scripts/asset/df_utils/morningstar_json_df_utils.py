from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns

db_name = ["loaded", "cleansed"]
data_source = "asset_morningstar_json"


def get_data_lineage(table_name, file_tag, isin_msid):
    return {
        'target_type': "lakehouse",
        'target_endpoint': table_name,
        'src0_type': "s3",
        'src0_endpoint': f"landing/asset/public_listed/morningstar/json/{isin_msid}/{file_tag.replace('_', '-')}",
        'etl_script_path': "ETL/scripts/asset/all_morningstar_json.py",
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


class LivePriceISINTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "live_price"
        self.date_format = {}
        self.explodables = {
            "category_broad_asset_class": ["Id", "Name"],
            "currency": ["Id"],
            "fund_attributes": ["HedgeFund"],
            "last_price": ["Currency.Id", "Date", "MarketDate", "MarketTime", "MarketTimeZone", "Value"],
            "trading_currency": ["Id"],
        }
        self.table_name = f"{db_name[0]}.{data_source}_isin_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name, self.file_tag, "isin")

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("dbgtime", LongType()),
            StructField("id", StringType()),
            StructField("isin", StringType()),
            StructField("investment_type", StringType()),
            StructField("exchange", StringType()),
            StructField("type", StringType()),
            StructField("name", StringType()),
            StructField("country", StringType()),
            StructField("legal_name", StringType()),
            StructField("company_name", StringType()),
            StructField("company_short_name", StringType()),
            StructField("net_change", DoubleType()),
            StructField("net_change_percent", DoubleType()),
            StructField("bid_price", DoubleType()),
            StructField("symbol", StringType()),
            StructField("ask_date_time", TimestampType()),
            StructField("ask_date", TimestampType()),
            StructField("ask_price", DoubleType()),
            StructField("average_volume", DoubleType()),
            StructField("bid_date_time", TimestampType()),
            StructField("currency_id", StringType()),
            StructField("domicile", StringType()),
            StructField("category_broad_asset_class_id", StringType()),
            StructField("category_broad_asset_class_name", StringType()),
            StructField("fund_attributes_hedge_fund", BooleanType()),
            StructField("fund_id", StringType()),
            StructField("fund_benchmark", StringType()),
            StructField("fund_share_class_status", IntegerType()),
            StructField("has_price_entitlement", BooleanType()),
            StructField("high_price", DoubleType()),
            StructField("inception_date", TimestampType()),
            StructField("is_oldest_share_class", StringType()),# BooleanType()),*
            StructField("is_primary", BooleanType()),
            StructField("last_price_currency_id", StringType()),
            StructField("last_price_date", TimestampType()),
            StructField("last_price_market_date", DateType()),
            StructField("last_price_market_time", StringType()),# TimeType()),* #(if the type exists)
            StructField("last_price_market_time_zone", StringType()),
            StructField("last_price_value", DoubleType()),
            StructField("last_volume", DoubleType()),
            StructField("legal_structure", StringType()),
            StructField("low_price", DoubleType()),
            StructField("management_fee", DoubleType()),
            StructField("ms_market_cap", DoubleType()),
            StructField("ongoing_charge", DoubleType()),
            StructField("open_price", DoubleType()),
            StructField("portfolios", StringType()),
            StructField("previous_close", DoubleType()),
            StructField("pricing_frequency", StringType()),
            StructField("purchase_details", StringType()),
            StructField("total_expense_ratio", DoubleType()),
            StructField("trading_currency_id", StringType()),
            StructField("trailing_performance", StringType()),
            StructField("bid_date", TimestampType()),
            StructField("currency_hedged", BooleanType()),
            StructField("currency_hedged_to", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class FullResponseISINTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "full_response"
        self.date_format = {}
        self.explodables = {
            "currency": ["Id"],
            "fund_attributes": ["HedgeFund"],
            "last_price": ["Currency.Id", "Date", "MarketDate", "MarketTime", "MarketTimeZone", "Value"],
            "trading_currency": ["Id"],
        }
        self.table_name = f"{db_name[0]}.{data_source}_isin_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name, self.file_tag, "isin")

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("dbgtime", LongType()),
            StructField("id", StringType()),
            StructField("isin", StringType()),
            StructField("investment_type", StringType()),
            StructField("exchange", StringType()),
            StructField("type", StringType()),
            StructField("name", StringType()),
            StructField("country", StringType()),
            StructField("legal_name", StringType()),
            StructField("company_name", StringType()),
            StructField("company_short_name", StringType()),
            StructField("net_change", DoubleType()),
            StructField("net_change_percent", DoubleType()),
            StructField("bid_price", DoubleType()),
            StructField("bid_date", TimestampType()),
            StructField("ask_date", TimestampType()),
            StructField("ask_price", DoubleType()),
            StructField("average_volume", DoubleType()),
            StructField("currency_id", StringType()),
            StructField("domicile", StringType()),
            StructField("fund_attributes_hedge_fund", BooleanType()),
            StructField("fund_id", StringType()),
            StructField("fund_share_class_status", IntegerType()),
            StructField("has_price_entitlement", BooleanType()),
            StructField("high_price", DoubleType()),
            StructField("inception_date", TimestampType()),
            StructField("is_primary", BooleanType()),
            StructField("last_volume", DoubleType()),
            StructField("legal_structure", StringType()),
            StructField("low_price", DoubleType()),
            StructField("ms_market_cap", DoubleType()),
            StructField("open_price", DoubleType()),
            StructField("portfolios", StringType()),
            StructField("previous_close", DoubleType()),
            StructField("pricing_frequency", StringType()),
            StructField("purchase_details", StringType()),
            StructField("symbol", StringType()),
            StructField("trading_currency_id", StringType()),
            StructField("trailing_performance", StringType()),
            StructField("management_fee", DoubleType()),
            StructField("fund_benchmark", StringType()),
            StructField("ongoing_charge", DoubleType()),
            StructField("category_broad_asset_class_id", StringType()),
            StructField("category_broad_asset_class_name", StringType()),
            StructField("total_expense_ratio", DoubleType()),
            StructField("is_oldest_share_class", BooleanType()),
            StructField("category_broad_asset_class", StringType()),
            StructField("currency_hedged", StringType()),
            StructField("currency_hedged_to", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class FullResponseMSIDTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "full_response"
        self.date_format = {}
        self.explodables = {
            "category_broad_asset_class": ["Id", "Name"],
            "currency": ["Id"],
            "fund_attributes": ["HedgeFund"],
            "trading_currency": ["Id"],
        }
        self.table_name = f"{db_name[0]}.{data_source}_msid_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name, self.file_tag, "msid")

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("dbgtime", LongType()),
            StructField("id", StringType()),
            StructField("fund_id", StringType()),
            StructField("is_primary", BooleanType()),
            StructField("inception_date", TimestampType()),
            StructField("isin", StringType()),
            StructField("investment_type", StringType()),
            StructField("is_oldest_share_class", BooleanType()),
            StructField("exchange", StringType()),
            StructField("type", StringType()),
            StructField("name", StringType()),
            StructField("legal_name", StringType()),
            StructField("company_name", StringType()),
            StructField("company_short_name", StringType()),
            StructField("ms_market_cap", DoubleType()),
            StructField("country", StringType()),
            StructField("has_price_entitlement", BooleanType()),
            StructField("fund_share_class_status", IntegerType()),
            StructField("domicile", StringType()),
            StructField("net_change", DoubleType()),
            StructField("net_change_percent", DoubleType()),
            StructField("ongoing_charge", DoubleType()),
            StructField("pricing_frequency", StringType()),
            StructField("ask_date", TimestampType()),
            StructField("ask_price", DoubleType()),
            StructField("average_volume", DoubleType()),
            StructField("bid_date", TimestampType()),
            StructField("bid_price", DoubleType()),
            StructField("category_broad_asset_class_id", StringType()),
            StructField("category_broad_asset_class_name", StringType()),
            StructField("currency_id", StringType()),
            StructField("fund_attributes_hedge_fund", BooleanType()),
            StructField("fund_benchmark", StringType()),
            StructField("high_price", DoubleType()),
            StructField("last_volume", DoubleType()),
            StructField("legal_structure", StringType()),
            StructField("low_price", DoubleType()),
            StructField("management_fee", DoubleType()),
            StructField("open_price", DoubleType()),
            StructField("portfolios", StringType()),
            StructField("previous_close", DoubleType()),
            StructField("purchase_details", StringType()),
            StructField("symbol", StringType()),
            StructField("total_expense_ratio", DoubleType()),
            StructField("trading_currency_id", StringType()),
            StructField("trailing_performance", StringType()),
            StructField("currency_hedged", StringType()),
            StructField("currency_hedged_to", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class MarketPriceMSIDTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "market_price"
        self.date_format = {}
        self.explodables = {
            "time_series": ["Security.Id", "Security.HistoryDetail[0].EndDate", "Security.HistoryDetail[0].Value"],
        }
        self.table_name = f"{db_name[1]}.{data_source}_msid_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name, self.file_tag, "msid")

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("time_series_security_id", StringType()),
            StructField("time_series_security_history_detail_end_date", DateType()),
            StructField("time_series_security_history_detail_value", DoubleType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class TotalReturnIndexMSIDTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "total_return_index"
        self.date_format = {}
        self.explodables = {
            "time_series": ["Security.Id", "Security.GrowthSeries[0].HistoryDetail[0].EndDate", "Security.GrowthSeries[0].HistoryDetail[0].Value"],
        }
        self.table_name = f"{db_name[1]}.{data_source}_msid_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name, self.file_tag, "msid")

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("time_series_security_id", StringType()),
            StructField("time_series_security_growth_series_history_detail_end_date", DateType()),
            StructField("time_series_security_growth_series_history_detail_value", DoubleType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
