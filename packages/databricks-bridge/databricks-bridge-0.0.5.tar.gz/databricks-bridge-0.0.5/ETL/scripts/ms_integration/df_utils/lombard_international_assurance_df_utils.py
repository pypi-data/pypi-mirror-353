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


class LombardInternationalAssuranceTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ";"
        self.file_tag = file_tag
        self.date_format = {"*": "yyyy-MM-dd"}
        self.column_line_index = 1
        self.column_line = []

        if file_tag == "solcpttit":
            self.table_tag = "asset"
        elif file_tag == "solcptcsh":
            self.table_tag = "cash"
        elif file_tag == "cshstmt":
            self.table_tag = "transactions"
            self.date_format = {"value_date": "yyyy-MM-dd", "accounting_date": "yyyy-MM-dd",
                                "cash_order_date_time": "yyyy-MM-dd HH:mm:ss"}
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.lombard_international_assurance_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/lombard_international_assurance"
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
        "asset": StructType([
            StructField("client_id", StringType()),
            StructField("value_date", DateType()),
            StructField("balance", StringType()),
            StructField("balance_at_value_date", StringType()),
            StructField("weighted_average_cost", StringType()),
            StructField("wac_currency", StringType()),
            StructField("accrued_interest", StringType()),  # *
            StructField("ai_currency", StringType()),
            StructField("cash_evaluation", StringType()),
            StructField("cash_evaluation_currency", StringType()),
            StructField("countervalue", StringType()),
            StructField("countervalue_currency", StringType()),
            StructField("kbl_code_identifying_security_used", StringType()),
            StructField("isin_code", StringType()),
            StructField("telekurs_code", StringType()),  # LongType()
            StructField("sedol_code", StringType()),  # *
            StructField("bloomberg_code", StringType()),  # *
            StructField("reuters_code", StringType()),  # *
            StructField("description_of_security", StringType()),
            StructField("type_of_financial_instrument", StringType()),
            StructField("complementary_type", StringType()),
            StructField("expression_type", StringType()),
            StructField("currency_code", StringType()),
            StructField("cash_evaluation_1", StringType()),  # *
            StructField("cash_evaluation_currency_1", StringType()),  # *
            StructField("vni_frequency", StringType()),
            StructField("place_of_listing", StringType()),
            StructField("calculation_basis", StringType()),
            StructField("contract_size", StringType()),
            StructField("strike_price", StringType()),
            StructField("currency_strike_price", StringType()),
            StructField("maturity_date", DateType()),
            StructField("interest_type", StringType()),
            StructField("interest_rate_in_percentage", StringType()),
            StructField("coupon_periodicity", StringType()),
            StructField("coupon_maturity", StringType()),
            StructField("issue_date", DateType()),
            StructField("issue_nominal_amount", StringType()),
            StructField("issue_nominal_amount_currency", StringType()),
            StructField("indicator_issue_emission", StringType()),
            StructField("indicateur_equalization_factor", StringType()),
            StructField("rating_s_and_p", StringType()),  # *
            StructField("economic_sector", StringType()),
            StructField("kbl_account_number", StringType()),
            StructField("account_name", StringType()),
            StructField("client_name", StringType()),
            StructField("lendability_indicator", StringType()),
            StructField("lendability_starting_date", StringType()),  # DateType()
            StructField("lendability_ending_date", StringType()),  # DateType()
            StructField("lendable_quantity", StringType()),  # LongType()
            StructField("lent_quantity", StringType()),  # LongType()
            StructField("price_without_factor", StringType()),  # *
            StructField("correction_factor", StringType()),  # *
        ]),
        "cash": StructType([
            StructField("client_id", StringType()),
            StructField("accounting_balance", StringType()),
            StructField("accounting_balance_1", StringType()),
            StructField("value_date", DateType()),
            StructField("balance_at_value_date", StringType()),
            StructField("balance_at_value_date_1", StringType()),
            StructField("exchange_values_rate", StringType()),
            StructField("last_booking_date", DateType()),
            StructField("iban", StringType()),
            StructField("kbl_cash_account_number", StringType()),
            StructField("client_name", StringType()),  # *
            StructField("account_title", StringType()),
            StructField("account_type", StringType()),
            StructField("account_currency", StringType()),
            StructField("future_date_d_plus1", DateType()),
            StructField("future_position_d_plus1", StringType()),
            StructField("future_date_d_plus2", DateType()),
            StructField("future_position_d_plus2", StringType()),
            StructField("future_date_d_plus3", DateType()),
            StructField("future_position_d_plus3", StringType()),
        ]),
        "transactions": StructType([
            StructField("client_id", StringType()),
            StructField("client_name", StringType()),
            StructField("account_title", StringType()),
            StructField("iban", StringType()),
            StructField("kbl_cash_account_number", StringType()),
            StructField("transaction_currency", StringType()),
            StructField("transaction_type", StringType()),
            StructField("transaction_reference", StringType()),
            StructField("transaction_name", StringType()),
            StructField("value_date", DateType()),
            StructField("accounting_date", DateType()),
            StructField("account_type", StringType()),
            StructField("movement_amount", StringType()),
            StructField("accounting_balance", StringType()),
            StructField("previous_balance", StringType()),
            StructField("statement_number", StringType()),  # *
            StructField("kbl_code_identifying_security_used", StringType()),  # *
            StructField("isin_code", StringType()),  # *
            StructField("telekurs_code", StringType()),  # *
            StructField("sedol_code", StringType()),  # *
            StructField("description_of_security", StringType()),  # *
            StructField("type_of_financial_instrument", StringType()),  # *
            StructField("complementary_type", StringType()),  # *
            StructField("expression_type", StringType()),  # *
            StructField("currency_code", StringType()),  # *
            StructField("vni_frequency", StringType()),  # *
            StructField("place_of_listing", StringType()),  # *
            StructField("calculation_basis", StringType()),  # *
            StructField("contract_size", StringType()),  # *
            StructField("strike_price", StringType()),  # *
            StructField("currency_strike_price", StringType()),  # *
            StructField("maturity_date", StringType()),  # *
            StructField("interest_type", StringType()),  # *
            StructField("interest_rate_in_percentage", StringType()),  # *
            StructField("coupon_periodicity_ddmm", StringType()),  # *
            StructField("coupon_maturity", StringType()),  # *
            StructField("issue_date", StringType()),  # *
            StructField("issue_nominal_amount", StringType()),  # *
            StructField("issue_nominal_amount_currency", StringType()),  # *
            StructField("indicator_issue_emission", StringType()),  # *
            StructField("indicateur_equalization_factor", StringType()),  # *
            StructField("rating_s_and_p", StringType()),  # *
            StructField("economic_sector", StringType()),  # *
            StructField("kbl_account_number", StringType()),  # *
            StructField("account_name", StringType()),  # *
            StructField("client_name_1", StringType()),  # *
            StructField("order_type", StringType()),  # *
            StructField("market_type", StringType()),  # *
            StructField("ordered_quantity", StringType()),  # *
            StructField("ordered_nominal_amount", StringType()),  # *
            StructField("ordered_nominal_amount_currency", StringType()),  # *
            StructField("ordered_amount", StringType()),  # *
            StructField("ordered_amount_currency", StringType()),  # *
            StructField("place_of_trade_mic_code", StringType()),  # *
            StructField("best_execution_indicator", StringType()),  # *
            StructField("client_reference", StringType()),  # *
            StructField("order_reference", StringType()),  # *
            StructField("deal_reference", StringType()),  # *
            StructField("order_date_time", StringType()),  # *
            StructField("prepye_indicator", StringType()),  # *
            StructField("prepye_amount", StringType()),  # *
            StructField("prepye_amount_currency", StringType()),  # *
            StructField("pool_factor", StringType()),  # *
            StructField("dirty_price_indicator", StringType()),  # *
            StructField("interest_accrued_days_number", StringType()),  # *
            StructField("tax_income_per_share", StringType()),  # *
            StructField("tax_income_per_share_currency", StringType()),  # *
            StructField("partially_execution_indicator", StringType()),  # *
            StructField("cancellation_indicator", StringType()),  # *
            StructField("quantity_settled", StringType()),  # *
            StructField("nominal_amount_settled", StringType()),  # *
            StructField("nominal_amount_settled_currency", StringType()),  # *
            StructField("averaged_gross_price", StringType()),  # *
            StructField("dealing_price_currency", StringType()),  # *
            StructField("trade_date_time", StringType()),  # *
            StructField("cash_settlement_date", StringType()),  # *
            StructField("gross_amount", StringType()),  # *
            StructField("gross_amount_currency", StringType()),  # *
            StructField("net_amount", StringType()),  # *
            StructField("net_amount_currency", StringType()),  # *
            StructField("securities_trade_list_costs_details", StringType()),  # *
            StructField("cash_order_number", StringType()),
            StructField("cash_order_client_number", StringType()),  # *
            StructField("client_reference_1", StringType()),
            StructField("cash_order_date_time", TimestampType()),
            StructField("remitter_account_number", StringType()),  # *
            StructField("remitter_bank_bic_code", StringType()),  # *
            StructField("remitter_bank_name", StringType()),  # *
            StructField("remitter_address1", StringType()),  # *
            StructField("remitter_address2", StringType()),  # *
            StructField("remitter_address3", StringType()),  # *
            StructField("remitter_address4", StringType()),  # *
            StructField("debitor_account_holder", StringType()),  # *
            StructField("debitor_account_number", StringType()),  # *
            StructField("debitor_cash_amount", StringType()),  # *
            StructField("debitor_cash_amount_currency", StringType()),  # *
            StructField("debitor_value_date", StringType()),  # *
            StructField("debitor_iblc_category", StringType()),  # *
            StructField("debitor_iblc_category_code", StringType()),  # *
            StructField("debitor_iblc_country_code", StringType()),  # *
            StructField("debitor_iblc_reason_code", StringType()),  # *
            StructField("debitor_advice_number", StringType()),  # *
            StructField("creditor_account_holder", StringType()),  # *
            StructField("creditor_account_number", StringType()),  # *
            StructField("creditor_iblc_category", StringType()),  # *
            StructField("creditor_iblc_category_code", StringType()),  # *
            StructField("creditor_iblc_country_code", StringType()),  # *
            StructField("creditor_iblc_reason_code", StringType()),  # *
            StructField("creditor_advice_number", StringType()),  # *
            StructField("beneficiary_name", StringType()),  # *
            StructField("beneficiary_account_number", StringType()),  # *
            StructField("beneficiary_bank_bic_code", StringType()),  # *
            StructField("beneficiary_bank_name", StringType()),  # *
            StructField("correspondent_bank_bic_code", StringType()),  # *
            StructField("correspondent_bank_name", StringType()),  # *
            StructField("communication1", StringType()),  # *
            StructField("communication2", StringType()),  # *
            StructField("communication3", StringType()),  # *
            StructField("communication4", StringType()),  # *
            StructField("charge_type", StringType()),  # *
            StructField("cash_order_list_costs_details", StringType()),  # *
            StructField("kbl_code_identifying_security_used_1", StringType()),  # *
            StructField("isin_code_1", StringType()),  # *
            StructField("telekurs_code_1", StringType()),  # *
            StructField("sedol_code_1", StringType()),  # *
            StructField("description_of_security_1", StringType()),  # *
            StructField("type_of_financial_instrument_1", StringType()),  # *
            StructField("complementary_type_1", StringType()),  # *
            StructField("expression_type_1", StringType()),  # *
            StructField("currency_code_1", StringType()),  # *
            StructField("vni_frequency_1", StringType()),  # *
            StructField("place_of_listing_1", StringType()),  # *
            StructField("calculation_basis_1", StringType()),  # *
            StructField("contract_size_1", StringType()),  # *
            StructField("strike_price_1", StringType()),  # *
            StructField("currency_strike_price_1", StringType()),  # *
            StructField("maturity_date_1", StringType()),  # *
            StructField("interest_type_1", StringType()),  # *
            StructField("interest_rate_in_percentage_1", StringType()),  # *
            StructField("coupon_periodicity_ddmm_1", StringType()),  # *
            StructField("coupon_maturity_1", StringType()),  # *
            StructField("issue_date_1", StringType()),  # *
            StructField("issue_nominal_amount_1", StringType()),  # *
            StructField("issue_nominal_amount_currency_1", StringType()),  # *
            StructField("indicator_issue_emission_1", StringType()),  # *
            StructField("indicateur_equalization_factor_1", StringType()),  # *
            StructField("rating_s_and_p_1", StringType()),  # *
            StructField("economic_sector_1", StringType()),  # *
            StructField("iban_1", StringType()),  # *
            StructField("kbl_account_number_1", StringType()),  # *
            StructField("client_name_2", StringType()),  # *
            StructField("account_title_1", StringType()),  # *
            StructField("account_type_1", StringType()),  # *
            StructField("account_currency", StringType()),  # *
            StructField("kbl_account_number_2", StringType()),  # *
            StructField("account_name_1", StringType()),  # *
            StructField("client_name_3", StringType()),  # *
            StructField("settlement_operation_status", StringType()),  # *
            StructField("counterparty_type", StringType()),  # *
            StructField("counterparty", StringType()),  # *
            StructField("securities_account_identifier", StringType()),  # *
            StructField("safekeeping_account_identifier", StringType()),  # *
            StructField("processing_reference", StringType()),  # *
            StructField("kb_operation_id", StringType()),  # *
            StructField("client_operation_reference", StringType()),  # *
            StructField("trade_status", StringType()),  # *
            StructField("trade_date", StringType()),  # *
            StructField("swift_notification_date", StringType()),  # *
            StructField("place_of_trade", StringType()),  # *
            StructField("settlement_date", StringType()),  # *
            StructField("effective_settlement_date", StringType()),  # *
            StructField("operation_direction", StringType()),  # *
            StructField("quantity", StringType()),  # *
            StructField("amount", StringType()),  # *
            StructField("amount_currency", StringType()),  # *
            StructField("deal_number", StringType()),  # *
            StructField("operation_type", StringType()),  # *
            StructField("deal_date", StringType()),  # *
            StructField("value_date_1", StringType()),  # *
            StructField("maturity_date_swaps_only", StringType()),  # *
            StructField("operation_direction_1", StringType()),  # *
            StructField("currency1", StringType()),  # *
            StructField("currency1_amount", StringType()),  # *
            StructField("counter_currency", StringType()),  # *
            StructField("counter_currency_amount", StringType()),  # *
            StructField("exchange_rate", StringType()),  # *
            StructField("forward_currency_amount_swaps_only", StringType()),  # *
            StructField("forward_counter_currency_amount_swaps_only", StringType()),  # *
            StructField("foreign_exchange_rate_swaps_only", StringType()),  # *
            StructField("profit_loss", StringType()),  # *
            StructField("profit_loss_currency", StringType()),  # *
            StructField("profit_loss_reference_rate", StringType()),  # *
            StructField("account_type_2", StringType()),  # *
            StructField("account_number", StringType()),  # *
            StructField("deal_number_1", StringType()),  # *
            StructField("operation_direction_2", StringType()),  # *
            StructField("deal_date_1", StringType()),  # *
            StructField("value_date_2", StringType()),  # *
            StructField("principal_currency", StringType()),  # *
            StructField("principal", StringType()),  # *
            StructField("interest_rate", StringType()),  # *
            StructField("calculation_basis_2", StringType()),  # *
            StructField("maturity_date_2", StringType()),  # *
            StructField("deposit_creation_reason", StringType()),  # *
            StructField("rollover_information", StringType()),  # *
            StructField("account_type_3", StringType()),  # *
            StructField("account_number_1", StringType()),  # *
            StructField("contract_reference", StringType()),  # *
            StructField("current_event_reference", StringType()),  # *
            StructField("operation_direction_3", StringType()),  # *
            StructField("deal_date_2", StringType()),  # *
            StructField("value_date_3", StringType()),  # *
            StructField("operation_currency", StringType()),  # *
            StructField("principal_amount", StringType()),  # *
            StructField("global_interest_rate", StringType()),  # *
            StructField("old_interest_rate", StringType()),  # *
            StructField("interests_processing_type", StringType()),  # *
            StructField("calculation_basis_3", StringType()),  # *
            StructField("maturity_date_3", StringType()),  # *
            StructField("maturity_amount", StringType()),  # *
            StructField("deposit_creation_reason_1", StringType()),  # *
            StructField("accrued_interests", StringType()),  # *
            StructField("capital_increased_with_contract", StringType()),  # *
            StructField("customer_deposit_list_costs_details", StringType()),  # *
            StructField("iban_2", StringType()),  # *
            StructField("kbl_account_number_3", StringType()),  # *
            StructField("client_name_4", StringType()),  # *
            StructField("account_title_2", StringType()),  # *
            StructField("account_type_4", StringType()),  # *
            StructField("account_currency_1", StringType()),  # *
            StructField("kbl_code_identifying_security_used_2", StringType()),  # *
            StructField("isin_code_2", StringType()),  # *
            StructField("telekurs_code_2", StringType()),  # *
            StructField("sedol_code_2", StringType()),  # *
            StructField("description_of_security_2", StringType()),  # *
            StructField("type_of_financial_instrument_2", StringType()),  # *
            StructField("complementary_type_2", StringType()),  # *
            StructField("expression_type_2", StringType()),  # *
            StructField("currency_code_2", StringType()),  # *
            StructField("vni_frequency_2", StringType()),  # *
            StructField("place_of_listing_2", StringType()),  # *
            StructField("calculation_basis_4", StringType()),  # *
            StructField("contract_size_2", StringType()),  # *
            StructField("strike_price_2", StringType()),  # *
            StructField("currency_strike_price_2", StringType()),  # *
            StructField("maturity_date_4", StringType()),  # *
            StructField("interest_type_2", StringType()),  # *
            StructField("interest_rate_in_percentage_2", StringType()),  # *
            StructField("coupon_periodicity_ddmm_2", StringType()),  # *
            StructField("coupon_maturity_2", StringType()),  # *
            StructField("issue_date_2", StringType()),  # *
            StructField("issue_nominal_amount_2", StringType()),  # *
            StructField("issue_nominal_amount_currency_2", StringType()),  # *
            StructField("indicator_issue_emission_2", StringType()),  # *
            StructField("indicateur_equalization_factor_2", StringType()),  # *
            StructField("rating_s_and_p_2", StringType()),  # *
            StructField("economic_sector_2", StringType()),  # *
            StructField("ca_reference", StringType()),  # *
            StructField("swift_official_reference", StringType()),  # *
            StructField("status_code", StringType()),  # *
            StructField("corporate_action_type_code", StringType()),  # *
            StructField("corporate_action_type_description", StringType()),  # *
            StructField("corporate_action_participation", StringType()),  # *
            StructField("execution_date", StringType()),  # *
            StructField("gross_amount_1", StringType()),  # *
            StructField("gross_amount_currency_1", StringType()),  # *
            StructField("net_amount_1", StringType()),  # *
            StructField("net_amount_currency_1", StringType()),  # *
            StructField("value_date_4", StringType()),  # *
            StructField("securities_quantity", StringType()),  # *
            StructField("rate", StringType()),  # *
            StructField("gross_amount_exchange_rate", StringType()),  # *
            StructField("customer_net_amount", StringType()),  # *
            StructField("customer_net_amount_currency", StringType()),  # *
            StructField("corporate_action_list_costs_details", StringType()),  # *
            StructField("instruction_type", StringType()),  # *
            StructField("instruction_external_reference", StringType()),  # *
            StructField("operation_external_reference", StringType()),  # *
            StructField("reception_date", StringType()),  # *
            StructField("instruction_origin", StringType()),  # *
            StructField("value_date_5", StringType()),  # *
            StructField("settlement_date_1", StringType()),  # *
            StructField("effective_settlement_date_1", StringType()),  # *
            StructField("source_securities_account", StringType()),  # *
            StructField("target_securities_account", StringType()),  # *
            StructField("securities_quantity_1", StringType()),  # *
        ]),
    }

    return spark_schema_dict[table_tag]
