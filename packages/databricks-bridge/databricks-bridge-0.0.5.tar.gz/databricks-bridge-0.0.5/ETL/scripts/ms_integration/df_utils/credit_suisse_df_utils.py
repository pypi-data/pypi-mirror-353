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


class CreditSuisseTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ";"
        self.file_tag = file_tag
        self.date_format = {"*": "yyyyMMdd"}
        self.column_line_index = 5
        self.column_line = []

        if file_tag == "cash":
            self.table_tag = file_tag
        elif file_tag == "security":
            self.table_tag = file_tag
        elif file_tag == "xml":
            self.table_tag = "headers"
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.credit_suisse_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/credit_suisse"
        etl_path = f"ETL/scripts/ms_integration/all_ms_integration_{'xml' if file_tag == 'xml' else 'csv_txt'}.py"
        self.data_lineage = get_data_lineage(self.table_name, s3_endpoint, etl_path)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    def get_dict_roi(self, dict_data):
        dict_data_roi = dict_data["psn:Document"]["PsNMoneyMarketContract"]
        dict_data_roi["Header"] = dict_data_roi.pop("Hdr:Header")
        return dict_data_roi

    def get_spark_schema(self):
        return non_essentialize_all_other_columns(get_table_schema(self.table_tag))

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


def get_table_schema(table_tag: str) -> StructType:
    spark_schema_dict = {
        "cash": StructType([
            StructField("technical_id", StringType()),  # LongType()
            StructField("message_type", StringType()),
            StructField("transaction_reference_number", StringType()),
            StructField("related_reference", StringType()),
            StructField("account_identification", StringType()),
            StructField("entry_number", StringType()),  # LongType()
            StructField("page_number", StringType()),  # LongType()
            StructField("opening_balance_amount_dc_mark", StringType()),
            StructField("opening_balance_amount_date", DateType()),
            StructField("opening_balance_currency", StringType()),
            StructField("opening_balance_amount", DoubleType()),
            StructField("value_date", DateType()),
            StructField("entry_date", StringType()),
            StructField("debit_credit_mark", StringType()),
            StructField("funds_code", StringType()),  # *
            StructField("amount", DoubleType()),
            StructField("transaction_type_identification_code", StringType()),
            StructField("reference_for_the_account_owner", StringType()),
            StructField("account_servicing_institutions_reference", StringType()),
            StructField("supplementary_details", StringType()),
            StructField("information_to_account_owner_line1", StringType()),
            StructField("information_to_account_owner_line2", StringType()),  # *
            StructField("information_to_account_owner_line3", StringType()),  # *
            StructField("information_to_account_owner_line4", StringType()),  # *
            StructField("information_to_account_owner_line5", StringType()),  # *
            StructField("information_to_account_owner_line6", StringType()),  # *
            StructField("closing_balance_amount_dc_mark", StringType()),
            StructField("closing_balance_amount_date", DateType()),
            StructField("closing_balance_currency", StringType()),
            StructField("closing_balance_amount", DoubleType()),
            StructField("closing_available_balance_dc_mark", StringType()),
            StructField("closing_available_balance_date", DateType()),
            StructField("closing_available_balance_currency", StringType()),
            StructField("closing_available_balance_amount", DoubleType()),
            StructField("forward_available_balance_dc_mark1", StringType()),
            StructField("forward_available_balance_date1", DateType()),
            StructField("forward_available_balance_currency1", StringType()),
            StructField("forward_available_balance_amount1", DoubleType()),
            StructField("forward_available_balance_dc_mark2", StringType()),  # *
            StructField("forward_available_balance_date2", StringType()),  # *
            StructField("forward_available_balance_currency2", StringType()),  # *
            StructField("forward_available_balance_amount2", StringType()),  # *
            StructField("forward_available_balance_dc_mark3", StringType()),  # *
            StructField("forward_available_balance_date3", StringType()),  # *
            StructField("forward_available_balance_currency3", StringType()),  # *
            StructField("forward_available_balance_amount3", StringType()),  # *
            StructField("forward_available_balance_dc_mark4", StringType()),  # *
            StructField("forward_available_balance_date4", StringType()),  # *
            StructField("forward_available_balance_currency4", StringType()),  # *
            StructField("forward_available_balance_amount4", StringType()),  # *
            StructField("forward_available_balance_dc_mark5", StringType()),  # *
            StructField("forward_available_balance_date5", StringType()),  # *
            StructField("forward_available_balance_currency5", StringType()),  # *
            StructField("forward_available_balance_amount5", StringType()),  # *
            StructField("forward_available_balance_dc_mark6", StringType()),  # *
            StructField("forward_available_balance_date6", StringType()),  # *
            StructField("forward_available_balance_currency6", StringType()),  # *
            StructField("forward_available_balance_amount6", StringType()),  # *
            StructField("forward_available_balance_dc_mark7", StringType()),  # *
            StructField("forward_available_balance_date7", StringType()),  # *
            StructField("forward_available_balance_currency7", StringType()),  # *
            StructField("forward_available_balance_amount7", StringType()),  # *
            StructField("forward_available_balance_dc_mark8", StringType()),  # *
            StructField("forward_available_balance_date8", StringType()),  # *
            StructField("forward_available_balance_currency8", StringType()),  # *
            StructField("forward_available_balance_amount8", StringType()),  # *
            StructField("forward_available_balance_dc_mark9", StringType()),  # *
            StructField("forward_available_balance_date9", StringType()),  # *
            StructField("forward_available_balance_currency9", StringType()),  # *
            StructField("forward_available_balance_amount9", StringType()),  # *
            StructField("forward_available_balance_dc_mark10", StringType()),  # *
            StructField("forward_available_balance_date10", StringType()),  # *
            StructField("forward_available_balance_currency10", StringType()),  # *
            StructField("forward_available_balance_amount10", StringType()),  # *
            StructField("information_to_account_owner_line1_whole_message", StringType()),  # *
            StructField("information_to_account_owner_line2_whole_message", StringType()),  # *
            StructField("information_to_account_owner_line3_whole_message", StringType()),  # *
            StructField("information_to_account_owner_line4_whole_message", StringType()),  # *
            StructField("information_to_account_owner_line5_whole_message", StringType()),  # *
            StructField("information_to_account_owner_line6_whole_message", StringType()),  # *
        ]),
        "security": StructType([
            StructField("technical_id", StringType()),  # LongType()
            StructField("message_type", StringType()),
            StructField("page_number", StringType()),
            StructField("continuation_indicator", StringType()),
            StructField("statement_number", StringType()),  # *
            StructField("function_of_the_message", StringType()),
            StructField("senders_message_reference", StringType()),
            StructField("preparation_date", DateType()),
            StructField("preparation_time", StringType()),  # *
            StructField("statement_date", DateType()),
            StructField("statement_time", StringType()),  # *
            StructField("statement_frequency_ind", StringType()),
            StructField("complete_updates_ind", StringType()),
            StructField("statement_type", StringType()),
            StructField("statement_basis", StringType()),
            StructField("related_message_reference", StringType()),
            StructField("account_type_code", StringType()),  # *
            StructField("safekeeping_account", StringType()),
            StructField("activity_flag", StringType()),
            StructField("sub_safekeeping_statement", StringType()),
            StructField("security_interest_lien_or_right_of_set_off", StringType()),  # *
            StructField("total_holdings_of_page_currency", StringType()),
            StructField("total_holdings_of_page", DoubleType()),
            StructField("total_holdings_of_statement_currency", StringType()),
            StructField("total_holdings_of_statement", DoubleType()),
            StructField("total_elegible_collateral_currency", StringType()),  # *
            StructField("total_elegible_collateral", StringType()),  # *
            StructField("isin", StringType()),
            StructField("instrument_identification1", StringType()),
            StructField("instrument_identification2", StringType()),
            StructField("instrument_identification3", StringType()),
            StructField("instrument_identification4", StringType()),
            StructField("fia_instrument_code_or_description", StringType()),  # *
            StructField("fiacfi_code", StringType()),  # *
            StructField("fia_option_style", StringType()),  # *
            StructField("fia_option_type", StringType()),  # *
            StructField("fia_currency_of_denomination", StringType()),
            StructField("fia_expiry_date", StringType()),  # *
            StructField("fia_maturity_date", DateType()),
            StructField("fia_valuation_haircut", StringType()),  # *
            StructField("fia_exercise_price_type_code", StringType()),  # *
            StructField("fia_exercise_price_currency", StringType()),  # *
            StructField("fia_exercise_price_amount", StringType()),  # *
            StructField("fia_contract_size_code", StringType()),
            StructField("fia_contract_size_quantity", DoubleType()),
            StructField("fiaisin_underlaying", StringType()),  # *
            StructField("fia_instrument_identification1", StringType()),  # *
            StructField("fia_instrument_identification2", StringType()),  # *
            StructField("fia_instrument_identification3", StringType()),  # *
            StructField("fia_instrument_identification4", StringType()),  # *
            StructField("market_price_type_code", StringType()),
            StructField("market_price", DoubleType()),
            StructField("market_price_currency", StringType()),
            StructField("price_quotation_date", DateType()),
            StructField("aggregate_quantity_type_code", StringType()),
            StructField("aggregate_balance", DoubleType()),
            StructField("available_quantity_type_code", StringType()),
            StructField("available_balance", DoubleType()),
            StructField("not_available_quantity_type_code", StringType()),  # *
            StructField("not_available_balance", DoubleType()),
            StructField("number_of_days_accrued", StringType()),  # *
            StructField("holding_value_currency", StringType()),
            StructField("holding_value", DoubleType()),
            StructField("accrued_interest_amount_cur", StringType()),  # *
            StructField("accrued_interest_amount", StringType()),  # *
            StructField("holdings_narrative_line1", StringType()),
            StructField("holdings_narrative_line2", StringType()),
            StructField("holdings_narrative_line3", StringType()),
            StructField("holdings_narrative_line4", StringType()),
            StructField("holdings_narrative_line5", StringType()),
            StructField("holdings_narrative_line6", StringType()),
            StructField("holdings_narrative_line7", StringType()),  # LongType()
            StructField("holdings_narrative_line8", StringType()),  # *
            StructField("holdings_narrative_line9", StringType()),  # *
            StructField("holdings_narrative_line10", StringType()),  # *
            StructField("subbal_quantity_type_code", StringType()),  # *
            StructField("subbal_on_loan_blanace", StringType()),  # *
            StructField("subbalcola_type_code", StringType()),  # *
            StructField("subbalcola_balance", StringType()),  # *
            StructField("subbal_place_safekeeping_code", StringType()),
            StructField("subbal_place_safekeeping_identifier", StringType()),
            StructField("subbal_type_code", StringType()),
            StructField("subbal_currency_code", StringType()),
            StructField("subbal_price", DoubleType()),
            StructField("subbal_number_of_days_accrued", StringType()),  # *
            StructField("subbal_holding_value_currency", StringType()),
            StructField("subbal_holding_value", DoubleType()),
            StructField("subbal_elegible_collateral_currency", StringType()),  # *
            StructField("subbal_elegible_collateral_value", StringType()),  # *
            StructField("subbal_exchange_rate_first_cur", StringType()),  # *
            StructField("subbal_exchange_rate_second_cur", StringType()),  # *
            StructField("subbal_exchange_rate", StringType()),  # *
            StructField("subbal_details_narrative_line1", StringType()),
            StructField("subbal_details_narrative_line2", StringType()),
            StructField("subbal_details_narrative_line3", StringType()),  # *
            StructField("subbal_details_narrative_line4", StringType()),  # *
            StructField("subbal2_quantity_type_code", StringType()),  # *
            StructField("subbal2_on_loan_blanace", StringType()),  # *
            StructField("subbal2_type_code", StringType()),  # *
            StructField("subbal2_currency_code", StringType()),  # *
            StructField("subbal2_price", StringType()),  # *
            StructField("subbal2_number_of_days_accrued", StringType()),  # *
            StructField("subbal2_holding_value_currency", StringType()),  # *
            StructField("subbal2_holding_value", StringType()),  # *
            StructField("subbal2_exchange_rate_first_cur", StringType()),  # *
            StructField("subbal2_exchange_rate_second_cur", StringType()),  # *
            StructField("subbal2_exchange_rate", StringType()),  # *
            StructField("subbal2_details_narrative_line1", StringType()),  # *
            StructField("subbal2_details_narrative_line2", StringType()),  # *
            StructField("subbal2_details_narrative_line3", StringType()),  # *
            StructField("subbal2_details_narrative_line4", StringType()),  # *
            StructField("fin_exchange_rate_first_cur", StringType()),
            StructField("fin_exchange_rate_second_cur", StringType()),
            StructField("fin_exchange_rate", DoubleType()),
            StructField("additional_text", StringType()),  # *
        ]),
        "headers": StructType([
            StructField("header_sndr_to_rcvr_inf_rcvr_bic", StringType()),
            StructField("header_sndr_to_rcvr_inf_sndr_bic", StringType()),
            StructField("header_fl_inf_dwh_msg_id", StringType()),
            StructField("header_fl_inf_location_iso2_cd", StringType()),
            StructField("header_fl_inf_crtn_dt_tm", TimestampType()),
            StructField("header_fl_inf_rprtng_dt", DateType()),
            StructField("header_fl_inf_type", StringType()),
            StructField("header_fl_inf_type_cd", StringType()),
            StructField("header_fl_inf_vrsn", StringType()),
            StructField("header_fl_inf_clnt_fmt", StringType()),
            StructField("header_fl_inf_msq_seq_no", StringType()),
            StructField("data_clnt_mm_data_clnt_key_int_rpt_unit", StringType()),
            StructField("data_clnt_mm_data_clnt_key_int_rpt_unit_desc", StringType()),
            StructField("data_clnt_mm_data_clnt_key_clnt_id", StringType()),
            StructField("data_clnt_mm_data_clnt_key_ext_clnt_id", StringType()),
            StructField("data_clnt_mm_data_mm_ctrct_inf", StringType()),
        ]),
    }

    return spark_schema_dict[table_tag]
