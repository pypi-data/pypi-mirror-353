from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns
from ETL.commons.ease_of_use_fcns import get_checkpoint_dir
import os

db_names = {
    "general_db": "general",
    "data_quality_score_db": "data_quality_score",
    "morningstar_db": "morningstar"
    }
checkpoint_dir = get_checkpoint_dir("sql_carousel")


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


class IsinMsidMappingTable(TablesDynamic):

    def __init__(self):
        self.class_name = "IsinMsidMapping"
        self.overwrite = False
        self.source_tables = {
            "isin": "loaded.asset_morningstar_json_isin_full_response",
            "msid": "loaded.asset_morningstar_json_msid_full_response"
        }
        self.table_name = f"{db_names['general_db']}.asset_isin_msid_mapping"
        self.prep_queries = []
        self.sql_query = f"""
            with isin_tbl as (
                select distinct "isin_tbl" tbl, id as msid, isin from {self.source_tables["isin"]}
            ), msid_tbl as (
                select distinct "msid_tbl" tbl, id as msid, isin from {self.source_tables["msid"]}
            ), unioned_tbl as (
                select tbl, isin, msid from isin_tbl
                union all
                select tbl, isin, msid from msid_tbl
            )
            select distinct isin, msid from unioned_tbl
            except
            select distinct isin, msid from {self.table_name}
        """
        
    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("isin", StringType()),
            StructField("msid", StringType()),
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class MorningstarAssetTable(TablesDynamic):

    def __init__(self):
        self.class_name = "MorningstarAsset"
        self.overwrite = True
        self.source_tables = {
            "json_full_response": "loaded.asset_morningstar_json_isin_full_response",
            "morningstar_dataoutput": "loaded.asset_morningstar_xml_isin_dataoutput",
            "legalstructure": "constants_v2.asset_legal_structure",
            "created_asset": "constants_v2.asset_legal_structure"
            
        }
        self.table_name = f"{db_names['morningstar_db']}.asset"
        self.prep_queries = []
        self.sql_query = f"""
            select {self.source_tables["json_full_response"]}.isin,
			 legal_name as name,
			 "" as description, 
			 nvl (Currency_id, 826) as base_currency,
			 null as benchmark_isin,
			 1 as y_benchmark_type,
			 nvl(fund_share_class__share_class_attributes:CurrencyHedged, 'FALSE') as is_currency_hedged,
			 null as risk_level,
			 now() as created_at,
			 current_user() as created_by,
			 now() as updated_at,
			 current_user() as updated_by,
			 null as update_owner,
			 'FALSE' as is_approved,
			 1 as billing_ratio,
			 nvl({self.source_tables["json_full_response"]}.domicile, "") as domicile,
			 holding_type as holding_type,
			 asset_legal_structure.id as legal_structure,
			 case when pricing_frequency = 'D$' then 1
			      when pricing_frequency = 'W$' then 2
			      when pricing_frequency = 'M$' then 3
			      when pricing_frequency = 'Q$' then 5
			      when pricing_frequency = 'a$' then 7
			      when pricing_frequency = 'N$' then 8
			 end as liquidity,
			 nvl(previous_close,0) as nav,
			 'MORNING_STAR' as source,
			 'NONE' as status,
			 null as proxy_isin,
			 case when fund_id is null then 'FALSE' else 'TRUE' end as is_fund,
			 case when fund_share_class__fund__fund_attributes:indexfund = 'true' then 'PASSIVE'
			 else 'ACTIVE' end as fund_type,
			 case when fund_share_class__international_feature:UKReportingFund is not null then 'true'
			      when fund_share_class__international_feature:UKReportingFund <> "" then 'true'
			      when fund_share_class__international_feature:UKReportingFund is null then 'false'
			      when fund_share_class__international_feature:UKReportingFund = "" then 'false'
			      else null end as uk_reporting_status
            from {self.source_tables["json_full_response"]}
            join {self.source_tables["morningstar_dataoutput"]} on {self.source_tables["json_full_response"]}.id = fund_share_class__id
            left join {self.source_tables["legalstructure"]} on value = legal_structure
            left join {self.source_tables["created_asset"]} on {self.source_tables["created_asset"]}.isin = {self.source_tables["json_full_response"]}.isin
        """

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("isin", StringType()),
            StructField("name", StringType()),
            StructField("description", StringType()),
            StructField("base_currency", StringType()),
            StructField("benchmark_isin", StringType()),
            StructField("y_benchmark_type", StringType()),
            StructField("is_currency_hedged", StringType()),
            StructField("risk_level", StringType()),
            StructField("created_at", TimestampType()),
            StructField("created_by", StringType()),
            StructField("updated_at", TimestampType()),
            StructField("updated_by", StringType()),
            StructField("update_owner", StringType()),
            StructField("is_approved", StringType()),
            StructField("billing_ratio", StringType()),
            StructField("domicile", StringType()),
            StructField("holding_type", StringType()),
            StructField("legal_structure", StringType()),
            StructField("liquidity", IntegerType()),
            StructField("nav", StringType()),
            StructField("source", StringType()),
            StructField("status", StringType()),
            StructField("proxy_isin", StringType()),
            StructField("fund_type", StringType()),
            StructField("uk_reporting_status", StringType()),
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class DataQualityScoreClientProfileTable(TablesDynamic):

    def __init__(self):
        self.class_name = "DataQualityScoreClientProfile"
        self.overwrite = False
        self.source_tables = {
            "client_profile": "data_quality_score.client_profile"
        }
        self.table_name = f"""{db_names['data_quality_score_db']}.client_profile_history"""
        
        self.prep_queries = [self.delete_current_day_records()]
        self.sql_query = f"""
          SELECT ID AS CLIENT_ID
			,profile_status_id
			,SCORE:CPD
			,SCORE:provider
			,SCORE:liquidity
			,SCORE:accountFee
			,SCORE:betaExposure
			,SCORE:currencyExposure
			,SCORE:listedAssetPrice
			,SCORE:unlistedAssetPrice
			,SCORE:assetFee
            ,current_date() as created_date
        from {self.source_tables["client_profile"]}
        """

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("profile_status_id", StringType()),
            StructField("CPD", StringType()),
            StructField("provider", StringType()),
            StructField("liquidity", StringType()),
            StructField("accountFee", StringType()),
            StructField("betaExposure", StringType()),
            StructField("currencyExposure", StringType()),
            StructField("listedAssetPrice", StringType()),
            StructField("unlistedAssetPrice", StringType()),
            StructField("assetFee", StringType()),
            StructField("created_date", TimestampType())     
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""    
    
    def delete_current_day_records(self):
        return f"""delete from {self.table_name} WHERE created_date = current_date();"""


class InstantiateTableClasses:
    def __init__(self):
        self.instantiate = [
            IsinMsidMappingTable(),
            DataQualityScoreClientProfileTable(),
            MorningstarAssetTable()
        ]
