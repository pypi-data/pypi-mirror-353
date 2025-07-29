from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns, essential_field

db_name = "cleansed"
data_source = "asset_cbonds_json"


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


def get_data_lineage(table_name):
    return {
        'target_type': "lakehouse",
        'target_endpoint': table_name,
        'src0_type': "s3",
        'src0_endpoint': f"landing/asset/public_listed/cbonds/json/{table_name.split('_')[-1]}",
        'etl_script_path': "ETL/scripts/asset/all_cbonds_json.py",
        'src1_type': "service",
        'src1_endpoint': "ms-datalake-connector",
        'src1_script_path': "src/main/kotlin/com/ytree/msdatalakeconnector/adapter/driver/kafka/listener/AssetEventListener.kt",
        'src2_type': "kafka",
        'src2_endpoint': "MS_DATALAKE_CONNECTOR_ASSET_EVENT_TOPIC",
        'src2_script_path': ""
    }


class EmissionTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "emission"
        self.table_name = f"{db_name}.{data_source}_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType(), metadata=essential_field),
            StructField("document_eng", StringType()),
            StructField("isin_code", StringType()),
            StructField("isin_code_144a", StringType()),
            StructField("isin_code_3", StringType()),
            StructField("early_redemption_date", StringType()),# TimestampType())*,
            StructField("maturity_date", DateType()),
            StructField("bbgid", StringType()),
            StructField("bbgid_composite", StringType()),
            StructField("bbgid_ticker", StringType()),
            StructField("currency_name", StringType()),
            StructField("status_name_eng", StringType()),
            StructField("announced_volume_new", StringType()),
            StructField("placed_volume_new", StringType()),
            StructField("outstanding_volume", StringType()),
            StructField("emitent_country_name_eng", StringType()),
            StructField("formal_emitent_country", StringType()),
            StructField("nominal_price", StringType()),
            StructField("outstanding_nominal_price", StringType()),
            StructField("eurobonds_nominal", StringType()),
            StructField("remaining_outstand_amount", StringType()),
            StructField("offert_date", DateType()),
            StructField("floating_rate", StringType()),
            StructField("reference_rate_name_eng", StringType()),
            StructField("margin", StringType()),
            StructField("update_time", TimestampType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class FlowsTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "flows"
        self.table_name = f"{db_name}.{data_source}_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("file_isin", StringType()),
            StructField("actual_payment_date", DateType()),
            StructField("coupon_num", StringType()),
            StructField("coupon_pik", StringType()),
            StructField("cupon_rate", StringType()),
            StructField("cupon_rate_date", TimestampType()),
            StructField("cupon_sum", StringType()),
            StructField("cupon_sum_eurobonds_nominal", StringType()),
            StructField("cupon_sum_integral_multiple", StringType()),
            StructField("cupon_sum_minimum_tradeable_unit", StringType()),
            StructField("date", DateType()),
            StructField("days_beetwen_coupons", StringType()),
            StructField("do_not_stop", StringType()),
            StructField("emission_id", StringType()),
            StructField("emission_currency_id", StringType()),
            StructField("emission_date_of_start_placing", DateType()),
            StructField("emission_date_of_end_placing", DateType()),
            StructField("emission_emitent_id", StringType()),
            StructField("emission_emitent_type_id", StringType()),
            StructField("emission_emitent_branch_id", StringType()),
            StructField("emission_emitent_country_id", StringType()),
            StructField("emission_emitent_country_region_id", StringType()),
            StructField("emission_emitent_country_subregion_id", StringType()),
            StructField("emission_eurobonds_nominal", StringType()),
            StructField("emission_integral_multiple", StringType()),
            StructField("emission_isin_code", StringType()),
            StructField("emission_isin_code_144a", StringType()),
            StructField("emission_kind_id", StringType()),
            StructField("emission_maturity_date", DateType()),
            StructField("emission_minimum_tradeable_unit", StringType()),
            StructField("emission_nominal_price", StringType()),
            StructField("nontrading_start_date", StringType()),# DateType()),*
            StructField("nontrading_stop_date", StringType()),# DateType()),*
            StructField("redemption_eurobonds_nominal", StringType()),
            StructField("redemption_integral_multiple", StringType()),
            StructField("redemtion", StringType()),
            StructField("start_date", TimestampType()),
            StructField("updating_date", TimestampType()),
            StructField("ss_bond_current_trading_grounds", StringType()),
            StructField("emission_bond_type", StringType()),
            StructField("floating_rate", StringType()),
            StructField("unscheduled", StringType()),
            StructField("emission_securitisation", StringType()),
            StructField("emission_mortgage_bonds", StringType()),
            StructField("emission_status_id", StringType()),
            StructField("multiplier", StringType()),
            StructField("more_eng", StringType()),
            StructField("more_ita", StringType()),
            StructField("more_pol", StringType()),
            StructField("more_rus", StringType()),
            StructField("cupon_basis_id", StringType()),
            StructField("actual_coupon_period", StringType()),
            StructField("pool_factor", StringType()),
            StructField("redemption_minimum_tradeable_unit", StringType()),
            StructField("redemption_percentage", StringType()),
            StructField("show_em", StringType()),
            StructField("show_ib", StringType()),
            StructField("show_pl", StringType()),
            StructField("show_ru", StringType()),
            StructField("show_ua", StringType()),
            StructField("record_date", StringType()),
            StructField("updated_at", TimestampType()),
            StructField("created_at", TimestampType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class TradingsTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "tradings"
        self.table_name = f"{db_name}.{data_source}_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("clearance_profit", StringType()),
            StructField("date", DateType()),
            StructField("document_eng", StringType()),
            StructField("dur", StringType()),
            StructField("dur_mod", StringType()),
            StructField("dur_mod_to", StringType()),
            StructField("dur_to", StringType()),
            StructField("emission_id", StringType()),
            StructField("indicative_price", StringType()),
            StructField("indicative_yield", StringType()),
            StructField("isin_code", StringType()),
            StructField("isin_code_144a", StringType()),
            StructField("isin_code_3", StringType()),
            StructField("trading_ground_id", StringType()),
            StructField("trading_ground_name_eng", StringType()),
            StructField("emission_kind_id", StringType()),
            StructField("emission_emitent_id", StringType()),
            StructField("emission_emitent_country_id", StringType()),
            StructField("emission_emitent_country_region_id", StringType()),
            StructField("emission_emitent_type_id", StringType()),
            StructField("board_id", StringType()),
            StructField("show_ru", StringType()),
            StructField("buying_quote", StringType()),
            StructField("selling_quote", StringType()),
            StructField("last_price", StringType()),
            StructField("open_price", StringType()),
            StructField("max_price", StringType()),
            StructField("min_price", StringType()),
            StructField("avar_price", StringType()),
            StructField("agreement_number", StringType()),
            StructField("mid_price", StringType()),
            StructField("overturn", StringType()),
            StructField("offer_date", StringType()),
            StructField("offer_profit", StringType()),
            StructField("clearance_profit_effect", StringType()),
            StructField("offer_profit_effect", StringType()),
            StructField("coupon_profit_effect", StringType()),
            StructField("clearance_profit_nominal", StringType()),
            StructField("offer_profit_nominal", StringType()),
            StructField("coupon_profit_nominal", StringType()),
            StructField("coupon_profit", StringType()),
            StructField("aci", StringType()),
            StructField("ytm_bid", StringType()),
            StructField("ytm_offer", StringType()),
            StructField("yto_bid", StringType()),
            StructField("yto_offer", StringType()),
            StructField("ytc_bid", StringType()),
            StructField("ytc_offer", StringType()),
            StructField("ytm_last", StringType()),
            StructField("yto_last", StringType()),
            StructField("ytc_last", StringType()),
            StructField("ytm_close", StringType()),
            StructField("yto_close", StringType()),
            StructField("ytc_close", StringType()),
            StructField("ytm_open", StringType()),
            StructField("ytm_max", StringType()),
            StructField("ytm_min", StringType()),
            StructField("clear_price", StringType()),
            StructField("marketprice", StringType()),
            StructField("marketprice2", StringType()),
            StructField("volume", StringType()),
            StructField("volume_money", StringType()),
            StructField("years_to_maturity", StringType()),
            StructField("years_to_offert", StringType()),
            StructField("pvbp", StringType()),
            StructField("pvbp_offer", StringType()),
            StructField("convexity", StringType()),
            StructField("convexity_offer", StringType()),
            StructField("admittedquote", StringType()),
            StructField("legalcloseprice", StringType()),
            StructField("dur_coupon", StringType()),
            StructField("g_spread", StringType()),
            StructField("t_spread", StringType()),
            StructField("t_spread_benchmark", StringType()),
            StructField("current_yield", StringType()),
            StructField("indicative_price_type", StringType()),
            StructField("indicative_yield_type", StringType()),
            StructField("bid_ask_spread", StringType()),
            StructField("update_time", TimestampType()),
            StructField("created_at", TimestampType()),
            StructField("updated_at", TimestampType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
