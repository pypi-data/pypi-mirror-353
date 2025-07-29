from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns

db_name = "loaded"
data_source = "asset_morningstar_xml"


def get_data_lineage(table_name, isin_msid):
    return {
        'target_type': "lakehouse",
        'target_endpoint': table_name,
        'src0_type': "s3",
        'src0_endpoint': f"landing/asset/public_listed/morningstar/xml/{isin_msid}/dataoutput",
        'etl_script_path': "ETL/scripts/asset/all_morningstar_xml.py",
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


class DataoutputISINTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "dataoutput"
        self.table_name = f"{db_name}.{data_source}_isin_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name, "isin")

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("fund_share_class__id", StringType()),
            StructField("fund_share_class__fund_id", StringType()),
            StructField("fund_share_class__status", StringType()),
            StructField("fund_share_class__client_specific", StringType()),
            StructField("fund_share_class__fund__id", StringType()),
            StructField("fund_share_class__fund__fund_attributes", StringType()),
            StructField("fund_share_class__fund__fund_basics", StringType()),
            StructField("fund_share_class__fund__fund_features", StringType()),
            StructField("fund_share_class__fund__fund_narratives", StringType()),
            StructField("fund_share_class__multilingual_variation", StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_attributes", StringType()),
            StructField(
                "fund_share_class__fund__closed_end_fund_operation__fund_management_history__administrator_list",
                StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_management_history__advisor_list",
                        StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_management_history__advocate_list",
                        StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_management_history__auditor_list",
                        StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_management_history__banker_list",
                        StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_management_history__broker_list",
                        StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_management_history__custodian_list",
                        StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_management_history__fund_company_list",
                        StringType()),
            StructField(
                "fund_share_class__fund__closed_end_fund_operation__fund_management_history__legal_counsel_list",
                StringType()),
            StructField(
                "fund_share_class__fund__closed_end_fund_operation__fund_management_history__listing_sponsor_list",
                StringType()),
            StructField(
                "fund_share_class__fund__closed_end_fund_operation__fund_management_history__placing_agent_list",
                StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_management_history__provider_company",
                        StringType()),
            StructField(
                "fund_share_class__fund__closed_end_fund_operation__fund_management_history__registered_office_list",
                StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_management_history__registrar_list",
                        StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_management_history__secretary_list",
                        StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_management_history__sub_advisor_list",
                        StringType()),
            StructField(
                "fund_share_class__fund__closed_end_fund_operation__fund_management_history__transfer_agent_list",
                StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_management_history__tax_advisor_list",
                        StringType()),
            StructField(
                "fund_share_class__fund__closed_end_fund_operation__fund_management_history__investment_manager_list",
                StringType()),
            StructField(
                "fund_share_class__fund__closed_end_fund_operation__fund_management_history__financial_advisor_list",
                StringType()),
            StructField(
                "fund_share_class__fund__closed_end_fund_operation__fund_narratives__investment_criteria__borrowing_limits",
                StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__fund_narratives__language_id",
                        StringType()),
            StructField("fund_share_class__fund__closed_end_fund_operation__operation", StringType()),
            StructField("fund_share_class__fund__dealing_schedule__dealing_time__cut_off_time_detail", StringType()),
            StructField("fund_share_class__fund__dealing_schedule__dealing_time__dealing_time_detail", StringType()),
            StructField("fund_share_class__fund__dealing_schedule__valuation_time__country_id", StringType()),
            StructField("fund_share_class__fund__dealing_schedule__valuation_time__value", StringType()),
            StructField("fund_share_class__fund__extended_property__dealing_schedule", StringType()),
            StructField("fund_share_class__fund__multilingual_variation", StringType()),
            StructField("fund_share_class__fund__international_feature", StringType()),
            StructField("fund_share_class__fund__collateral_master_portfolio_id", StringType()),
            StructField("fund_share_class__fund__master_portfolio_id", StringType()),
            StructField("fund_share_class__fund__portfolio_list", StringType()),
            StructField("fund_share_class__fund__strategy_id", StringType()),
            StructField("fund_share_class__international_feature", StringType()),
            StructField("fund_share_class__operation__annual_report", StringType()),
            StructField("fund_share_class__operation__country_of_sales__sales_area", StringType()),
            StructField("fund_share_class__operation__prospectus__date", StringType()),
            StructField("fund_share_class__operation__prospectus__latest_prospectus_date", StringType()),
            StructField("fund_share_class__operation__prospectus__actual_front_load", StringType()),
            StructField("fund_share_class__operation__prospectus__actual_management_fee", StringType()),
            StructField("fund_share_class__operation__prospectus__administrative_fee", StringType()),
            StructField("fund_share_class__operation__prospectus__distribution_fee", StringType()),
            StructField("fund_share_class__operation__prospectus__custodian_fee", StringType()),
            StructField("fund_share_class__operation__prospectus__maximum_custodian_fee", StringType()),
            StructField("fund_share_class__operation__prospectus__management_fee", StringType()),
            StructField("fund_share_class__operation__prospectus__performance_fee", StringType()),
            StructField("fund_share_class__operation__prospectus__switching_fee", StringType()),
            StructField("fund_share_class__operation__prospectus__transaction_fee", StringType()),
            StructField("fund_share_class__operation__prospectus__subscription_fee", StringType()),
            StructField("fund_share_class__operation__prospectus__other_fee", StringType()),
            StructField("fund_share_class__operation__prospectus__expense_ratio", StringType()),
            StructField("fund_share_class__operation__prospectus__fee_negotiable", StringType()),
            StructField("fund_share_class__operation__prospectus__operating_expense_ratio", StringType()),
            StructField("fund_share_class__operation__purchase__purchase_detail", StringType()),
            StructField("fund_share_class__operation__purchase__platform_list", StringType()),
            StructField("fund_share_class__operation__share_class_basics", StringType()),
            StructField("fund_share_class__proprietary_data__aggregated_holding_currency", StringType()),
            StructField("fund_share_class__proprietary_data__aggregated_holding_geographic_zone", StringType()),
            StructField("fund_share_class__proprietary_data__currency", StringType()),
            StructField("fund_share_class__proprietary_data__geographic_zone", StringType()),
            StructField("fund_share_class__proprietary_data__latest_documents", StringType()),
            StructField("fund_share_class__proprietary_data__latest_documents__document_type", StringType()),
            StructField("fund_share_class__regulation", StringType()),
            StructField("fund_share_class__share_class_attributes", StringType()),
            StructField("fund_share_class__strategy__id", StringType()),
            StructField("fund_share_class__strategy__investment_approach", StringType()),
            StructField("fund_share_class__strategy__status", StringType()),
            StructField("fund_share_class__strategy__strategy_basics", StringType()),
            StructField("fund_share_class__strategy__strategy_attributes", StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__company_attributes",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__managed_portfolio",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__gips_compliance",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__disciplinarity",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__trading_policy",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__load_reduction__date",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__load_reduction__exchange_privilege",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__load_reduction__reinstatement_privilege",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__load_reduction__letter_of_intent",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__load_reduction__rights_of_accumulation__calculation_method_id",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__load_reduction__rights_of_accumulation__roa_qualification__account_list",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__load_reduction__rights_of_accumulation__roa_qualification__balance_aggregation",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__load_reduction__rights_of_accumulation__roa_qualification__owner_list",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__load_reduction__rights_of_accumulation__roa_qualification__reduction",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__load_reduction__rights_of_accumulation__other_consideration",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__regulatory_registration",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__trading_policy__excessive_trading_policy__date",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__asset_management_feature__trading_policy__excessive_trading_policy__policy_description",
                StringType()),
            StructField("fund_share_class__strategy__strategy_management__provider_company__company__branding_id",
                        StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__company_narratives",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__company_operation__company_attributes",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__company_operation__company_basics",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__company_operation__company_identifiers",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__company_operation__company_ownership",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__company_operation__key_personnel_list",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__company_operation__personnel_summary",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__company_operation__business_type_classification",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__company_operation__top_client_list",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__headquarter__country_headquarter",
                StringType()),
            StructField("fund_share_class__strategy__strategy_management__provider_company__company__id", StringType()),
            StructField("fund_share_class__strategy__strategy_management__provider_company__company__status",
                        StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__is_multi_identifiers",
                StringType()),
            StructField(
                "fund_share_class__strategy__strategy_management__provider_company__company__is_ultimate_parent",
                StringType()),
            StructField("fund_share_class__strategy__strategy_management__provider_company__company__legacy_family_id",
                        StringType()),
            StructField("fund_share_class__strategy__strategy_management__percent_from_external_research",
                        StringType()),
            StructField("fund_share_class__strategy__strategy_management__contractual_limit", StringType()),
            StructField("fund_share_class__strategy__strategy_management__minimum_investment", StringType()),
            StructField("fund_share_class__strategy__strategy_management__strategy_availability", StringType()),
            StructField("fund_share_class__trading_information__exchange_listing", StringType()),
            StructField("fund_share_class__trading_information__ip_o__currency_id", StringType()),
            StructField("fund_share_class__trading_information__ip_o__date", StringType()),
            StructField("fund_share_class__trading_information__ip_o__exchange", StringType()),
            StructField("fund_share_class__trading_information__ip_o__ipo_asset_raised", StringType()),
            StructField("fund_share_class__trading_information__ip_o__ipo_extra_share_issued", StringType()),
            StructField("fund_share_class__trading_information__ip_o__ipo_manager_shares", StringType()),
            StructField("fund_share_class__trading_information__ip_o__ipo_net_assets_raised", StringType()),
            StructField("fund_share_class__trading_information__ip_o__ipo_share_publicly_traded", StringType()),
            StructField("fund_share_class__trading_information__ip_o__ipo_warrants", StringType()),
            StructField("fund_share_class__trading_information__ip_o__nav", StringType()),
            StructField("fund_share_class__trading_information__ip_o__offer_price", StringType()),
            StructField("fund_share_class__trading_information__leverage_method__bank_credit", StringType()),
            StructField("fund_share_class__trading_information__leverage_method__futures", StringType()),
            StructField("fund_share_class__trading_information__leverage_method__margin_borrowing", StringType()),
            StructField("fund_share_class__trading_information__leverage_method__option", StringType()),
            StructField("fund_share_class__trading_information__leverage_method__swap", StringType()),
            StructField("status_code", StringType()),
            StructField("status_message", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class DataoutputMSIDTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "dataoutput"
        self.table_name = f"{db_name}.{data_source}_msid_{self.file_tag}"
        self.data_lineage = get_data_lineage(self.table_name, "msid")

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType(list(DataoutputISINTable.get_spark_schema())[:-4] + [ #[:-4] to avoid status_code, status_message, file_arrival_date and file_path fields
            StructField("policy__id", StringType()),
            StructField("policy__international_feature", StringType()),
            StructField("policy__policy_attributes__group_policy", StringType()),
            StructField("policy__policy_attributes__limited_availability", StringType()),
            StructField("policy__policy_attributes__non_group_policy", StringType()),
            StructField("policy__policy_attributes__partial_annuitization", StringType()),
            StructField("policy__policy_attributes__terminal_funding", StringType()),
            StructField("policy__policy_basics__currency__id", StringType()),
            StructField("policy__policy_basics__currency__value", StringType()),
            StructField("policy__policy_basics__domicile__id", StringType()),
            StructField("policy__policy_basics__domicile__value", StringType()),
            StructField("policy__policy_basics__isin", StringType()),
            StructField("policy__policy_basics__inception_date", StringType()),
            StructField("policy__policy_basics__legal_name", StringType()),
            StructField("policy__policy_basics__name", StringType()),
            StructField("policy__policy_basics__policy_type__id", StringType()),
            StructField("policy__policy_basics__policy_type__value", StringType()),
            StructField("policy__status", StringType()),
            StructField("policy__trading_information__exchange_listing", StringType()),
            StructField("sub_account__client_specific", StringType()),
            StructField("sub_account__id", StringType()),
            StructField("sub_account__policy_id", StringType()),
            StructField("sub_account__proprietary_data__aggregated_holding_currency", StringType()),
            StructField("sub_account__proprietary_data__aggregated_holding_geographic_zone", StringType()),
            StructField("sub_account__proprietary_data__currency", StringType()),
            StructField("sub_account__proprietary_data__geographic_zone", StringType()),
            StructField("sub_account__proprietary_data__latest_documents", StringType()),
            StructField("sub_account__status", StringType()),
            StructField("sub_account__sub_account_basics__inception_date", StringType()),
            StructField("sub_account__sub_account_basics__legal_name", StringType()),
            StructField("sub_account__sub_account_basics__name", StringType()),
            StructField("status_code", StringType()),
            StructField("status_message", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
