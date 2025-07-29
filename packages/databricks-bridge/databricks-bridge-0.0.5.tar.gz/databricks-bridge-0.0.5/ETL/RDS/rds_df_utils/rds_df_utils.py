from abc import ABC, abstractmethod
import os
from ETL.commons.ease_of_use_fcns import get_checkpoint_dir

db_name = "logging"
checkpoint_dir = get_checkpoint_dir("rds_integration")


class TablesDynamic(ABC):
    @abstractmethod
    def create_table(self):
        raise NotImplementedError

    @abstractmethod
    def delete_table(self):
        raise NotImplementedError

    @staticmethod
    def get_rds_tables_dict():
        raise NotImplementedError


class RDSConfigTable(TablesDynamic):

    def __init__(self, suffix=""):
        self.table_name = f"{db_name}.rds_table_ingestion_config{suffix}"
        self.permitted_groups = ["analysts"]

    def create_table(self):
        return f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id                          STRING NOT NULL,
            table_name                  STRING NOT NULL,
            table_schema                STRING NOT NULL,
            table_unique_identifier     STRING NOT NULL,
            constant                    BOOLEAN NOT NULL,
            updated_at                  TIMESTAMP NOT NULL,
            dataframe_schema            STRING NOT NULL,
            active                      BOOLEAN NOT NULL
        )
        {"TBLPROPERTIES (DELTA.enableChangeDataFeed = true)" if os.environ.get('ISDATABRICKS', 'local') == "TRUE" else "USING org.apache.spark.sql.parquet"};
        """

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""

    @staticmethod
    def get_rds_tables_dict():
        return [
            {"table_name": "advice.action_state",                                       "unq_id": "id",                        "constant": True,      "exclude_columns": []},
            {"table_name": "advice.advice_plan",                                        "unq_id": "id",                        "constant": True},
            {"table_name": "advice.state",                                              "unq_id": "id",                        "constant": True},
            {"table_name": "assets.asset",                                              "unq_id": "isin",                      "constant": True},
            {"table_name": "assets.asset_public",                                       "unq_id": "asset_isin",                "constant": True},
            {"table_name": "assets.beta_exposure",                                      "unq_id": "asset_isin",                "constant": True},
            {"table_name": "assets.beta_exposure_hist",                                 "unq_id": "asset_isin",                "constant": True},
            {"table_name": "assets.class",                                              "unq_id": "asset_isin",                "constant": True},
            {"table_name": "assets.currency_exposure",                                  "unq_id": "asset_isin",                "constant": True},
            {"table_name": "assets.country_exposure",                                   "unq_id": "asset_isin",                "constant": True},
            {"table_name": "assets.fee",                                                "unq_id": "asset_isin",                "constant": True},
            {"table_name": "assets.market_value",                                       "unq_id": "asset_isin",                "constant": True},
            {"table_name": "assets.total_return_index",                                 "unq_id": "asset_isin",                "constant": True},
            {"table_name": "client_asset.adjusted_asset_attributes",                    "unq_id": "asset_isin",                "constant": True},
            {"table_name": "client_financials.client_account_portfolio",                "unq_id": "id",                        "constant": True},
            {"table_name": "client_financials.client_accounts",                         "unq_id": "id",                        "constant": True},
            {"table_name": "client_financials.client_providers",                        "unq_id": "id",                        "constant": True},
            {"table_name": "client_financials.transaction",                             "unq_id": "id",                        "constant": True},
            {"table_name": "client_financials.contract",                                "unq_id": "id",                        "constant": True},
            {"table_name": "currency.rate_usd",                                         "unq_id": "code",                      "constant": True},
            {"table_name": "client_financials.financial_account_fee",                   "unq_id": "id",                        "constant": True},
            {"table_name": "client_financials.statement",                               "unq_id": "id",                        "constant": True},
            {"table_name": "client_financials.statement_line",                          "unq_id": "id",                        "constant": True},
            {"table_name": "client_portal.data_onboarding_state",                       "unq_id": "id",                        "constant": True},
            {"table_name": "client_portal.client_profile",                              "unq_id": "id",                        "constant": True},
            {"table_name": "client_portal.client_profile_settings",                     "unq_id": "id",                        "constant": True},
            {"table_name": "client_portal.client_provider",                             "unq_id": "id",                        "constant": True},  
            {"table_name": "client_portal.flyway_schema_history",                       "unq_id": "id",                        "constant": True},
            {"table_name": "client_portal.shared_document",                             "unq_id": "file_id",                   "constant": True},
            {"table_name": "client_portal.statements_upload",                           "unq_id": "id",                        "constant": True},
            {"table_name": "client_portal.welcome_message_show_case",                   "unq_id": "individual_user_id",        "constant": True},
            {"table_name": "company_stock_option.exercise",                             "unq_id": "id",                        "constant": True},
            {"table_name": "company_stock_option.info",                                 "unq_id": "id",                        "constant": True},
            {"table_name": "company_stock_option.vesting_percent",                      "unq_id": "id",                        "constant": True},
            {"table_name": "constants_v2.currency",                                     "unq_id": "id",                        "constant": True},
            {"table_name": "constants_v2.provider",                                     "unq_id": "id",                        "constant": True},
            {"table_name": "constants_v2.client_profile_status",                        "unq_id": "id",                        "constant": True},
            {"table_name": "constants_v2.financial_data_statement_source",              "unq_id": "id",                        "constant": True},
            {"table_name": "currency.rate_usd",                                         "unq_id": "code",                      "constant": True},
            {"table_name": "data_quality_score.client_profile",                         "unq_id": "id",                        "constant": True},
            {"table_name": "profiles.bo_user",                                          "unq_id": "id",                        "constant": True},
            {"table_name": "profiles.client_user",                                      "unq_id": "id",                        "constant": True},
            {"table_name": "profiles.general_info",                                     "unq_id": "client_id",                 "constant": True},
            {"table_name": "profiles.pod",                                              "unq_id": "id",                        "constant": True},
            {"table_name": "profiles.pod_client_relations",                             "unq_id": "pod_id",                    "constant": True},
            {"table_name": "profiles.client_user_profile",                              "unq_id": "pod_id",                    "constant": True},
            {"table_name": "risk_rebalancing.actual_risk_alerts_muting",                "unq_id": "profile_id",                "constant": True},
            {"table_name": "risk_rebalancing.client_profile_targets_history",           "unq_id": "profile_id",                "constant": True},
            {"table_name": "risk_rebalancing.financial_data_history",                   "unq_id": "profile_id",                "constant": True},
            {"table_name": "investment_solution.client_solution_daily_values",          "unq_id": "client_id",                 "constant": True},
            {"table_name": "investment_solution.asset",                                 "unq_id": "isin",                      "constant": True},
            {"table_name": "investment_solution.asset_daily_market_price",              "unq_id": "isin",                      "constant": True},
            {"table_name": "investment_solution.asset_daily_total_return_index",        "unq_id": "isin",                      "constant": True},
            {"table_name": "investment_solution.solution",                              "unq_id": "id",                        "constant": True},
            {"table_name": "investment_solution.client_solution_calculated",            "unq_id": "client_id",                 "constant": True},
            {"table_name": "Chat_v2.announcement",                                      "unq_id": "id",                        "constant": True},
            {"table_name": "Chat_v2.attachment_v3",                                     "unq_id": "id",                        "constant": True},
            {"table_name": "Chat_v2.broadcasting",                                      "unq_id": "id",                        "constant": True},
            {"table_name": "Chat_v2.channel_participant_v3",                            "unq_id": "channel_id",                "constant": True},
            {"table_name": "Chat_v2.channel_v3",                                        "unq_id": "id",                        "constant": True},
            {"table_name": "Chat_v2.file_metadata_v3",                                  "unq_id": "file_id",                   "constant": True},
            {"table_name": "Chat_v2.message",                                           "unq_id": "id",                        "constant": True},
            {"table_name": "Chat_v2.message_details_v3",                                "unq_id": "id",                        "constant": True},
            {"table_name": "Chat_v2.message_Status_v3",                                 "unq_id": "id",                        "constant": True},
            {"table_name": "Chat_v2.message_v3",                                        "unq_id": "id",                        "constant": True},
            {"table_name": "Chat_v2.participant_v3",                                    "unq_id": "id",                        "constant": True},
            {"table_name": "Chat_v2.user",                                              "unq_id": "id",                        "constant": True},
            {"table_name": "assets.review_status",                                      "unq_id": "asset_isin",                "constant": True},
            {"table_name": "operational.trade",                                         "unq_id": "id",                        "constant": True},
            {"table_name": "operational.transfer",                                      "unq_id": "id",                        "constant": True},
            {"table_name": "investment_solution.fund",                                  "unq_id": "isin",                      "constant": True},
            {"table_name": "private_equity.asset_data",                                 "unq_id": "isin",                      "constant": True},
            {"table_name": "private_equity.future_commitment",                          "unq_id": "id",                        "constant": True},
            {"table_name": "private_equity.client_asset",                               "unq_id": "id",                        "constant": True},
            {"table_name": "private_equity.client_statement",                           "unq_id": "id",                        "constant": True},
            {"table_name": "private_equity.client_portfolio",                           "unq_id": "id",                        "constant": True},
            {"table_name": "private_equity.projected_capital_calls",                    "unq_id": "id",                        "constant": True},
            {"table_name": "soft_facts.soft_fact",                                      "unq_id": "id",                        "constant": True},
            {"table_name": "assets.alternative_names",                                  "unq_id": "id",                        "constant": True},
            {"table_name": "advice_snapshot.advice_plan_details_snapshot",              "unq_id": "id",                        "constant": True},
            {"table_name": "advice.action_statement",                                   "unq_id": "id",                        "constant": True},
            {"table_name": "advice.label",                                              "unq_id": "id",                        "constant": True},
            {"table_name": "advice.label_category",                                     "unq_id": "id",                        "constant": True},
            {"table_name": "advice.advice_plan_labels",                                 "unq_id": "id",                        "constant": True},
            {"table_name": "constants_v2.financial_data_account_type",                  "unq_id": "id",                        "constant": True},
            {"table_name": "cpd.cpd_cache_provider_performance_details",                "unq_id": "client_id",                 "constant": True},
            {"table_name": "cpd.cpd_cache_provider_portfolio_performance_details",      "unq_id": "client_id",                 "constant": True},
            {"table_name": "cpd.info",                                                  "unq_id": "client_id",                 "constant": True},
            {"table_name": "cpd.process_history",                                       "unq_id": "client_id",                 "constant": True},
            {"table_name": "investment_solution.solution_calculated",                   "unq_id": "investment_solution_id",    "constant": True},
            {"table_name": "operational.archived_account",                              "unq_id": "id",                        "constant": True},
            {"table_name": "operational.archived_asset",                                "unq_id": "id",                        "constant": True},
            {"table_name": "ms_data_quality.asset_exclusions",                          "unq_id": "id",                        "constant": True},
            {"table_name": "ms_data_quality.muted_asset_rules",                         "unq_id": "id",                        "constant": True},
            {"table_name": "client_timeline.actions",                                   "unq_id": "id",                        "constant": True},
            {"table_name": "operational.account_transfer",                              "unq_id": "id",                        "constant": True},
            {"table_name": "operational.asset",                                         "unq_id": "isin",                      "constant": True},
            {"table_name": "operational.change_record",                                 "unq_id": "id",                        "constant": True},
            {"table_name": "operational.field_change",                                  "unq_id": "id",                        "constant": True},
            {"table_name": "operational.group",                                         "unq_id": "id",                        "constant": True},
            {"table_name": "operational.recommendation_group",                          "unq_id": "recommendation_group_id",   "constant": True},
            {"table_name": "operational.transfer_step",                                 "unq_id": "id",                        "constant": True},
            {"table_name": "operational.transfer_step_group",                           "unq_id": "id",                        "constant": True},
            {"table_name": "operational.transfer_step_history",                         "unq_id": "id",                        "constant": True},
            {"table_name": "advice.client_approved_actions_var_risk",                   "unq_id": "id",                        "constant": True},
            {"table_name": "profiles.client_bo_user_relations",                         "unq_id": "id",                        "constant": True},
            # {"table_name": "rps_aggregator.client_rps_monitoring",                      "unq_id": "id",                        "constant": True},
            {"table_name": "trading_restrictions.allowed_asset",                        "unq_id": "id",                        "constant": True},
            {"table_name": "trading_restrictions.allowed_investment_solution",          "unq_id": "id",                        "constant": True},
            {"table_name": "trading_restrictions.allowed_provider",                     "unq_id": "id",                        "constant": True},
            {"table_name": "trading_restrictions.client_profile_trading_restriction",   "unq_id": "id",                        "constant": True},
            {"table_name": "trading_restrictions.trading_restriction",                  "unq_id": "id",                        "constant": True},
            {"table_name": "fps.fps_common",                                            "unq_id": "id",                        "constant": True},
            {"table_name": "fps.fps_v2",                                                "unq_id": "id",                        "constant": True},
            {"table_name": "debt.info",                                                 "unq_id": "id",                        "constant": True},
            {"table_name": "debt.interest_rate",                                        "unq_id": "id",                        "constant": True},
            {"table_name": "debt.interest_rate_reference",                              "unq_id": "id",                        "constant": True},
            {"table_name": "fps.fps_v3",                                                "unq_id": "id",                        "constant": True},
            {"table_name": "private_asset_property.valuation",                          "unq_id": "isin",                      "constant": True},
            {"table_name": "private_asset_other.price",                                 "unq_id": "isin",                      "constant": True},
        ]
