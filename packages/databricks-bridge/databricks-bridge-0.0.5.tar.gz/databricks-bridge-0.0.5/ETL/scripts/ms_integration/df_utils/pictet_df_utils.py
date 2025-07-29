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


class PictetTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = "\t"
        self.file_tag = file_tag
        self.date_format = {"*": "yyyyMMdd"}
        self.column_line_index = 2
        self.column_line = []

        if file_tag == "de":
            self.table_tag = "positions"
        elif file_tag == "tr":
            self.table_tag = "transactions"
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.pictet_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/pictet"
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
        "positions": StructType([
            StructField("portfolio_number", StringType()),
            StructField("valuation_currency", StringType()),
            StructField("nominal_currency", StringType()),
            StructField("quantity", DoubleType()),
            StructField("security_description", StringType()),
            StructField("isin", StringType()),  # *
            StructField("sedol", StringType()),  # *
            StructField("telekurs", StringType()),  # *
            StructField("cusip", StringType()),  # *
            StructField("pictet_sec_number", StringType()),  # *
            StructField("market_price_currency", StringType()),  # *
            StructField("market_price", StringType()),  # *
            StructField("market_price_code", StringType()),  # *
            StructField("market_price_date", StringType()),  # DateType()
            StructField("security_net_cost_ccy", StringType()),  # *
            StructField("total_net_cost_sec_ccy", DoubleType()),
            StructField("total_net_cost_val_ccy", DoubleType()),
            StructField("market_val_without_acc_int", DoubleType()),
            StructField("accrued_int", DoubleType()),
            StructField("market_val_with_acc_int", DoubleType()),
            StructField("fx_rate_sec_vs_val", DoubleType()),
            StructField("type_code", StringType()),  # *
            StructField("fx_rate_price_vs_val", DoubleType()),
            StructField("type_code_1", StringType()),  # *
            StructField("financial_instr_code", StringType()),
            StructField("fin_instr_code_description", StringType()),
            StructField("secc_currrisk_code", StringType()),  # *
            StructField("country_risk_code", StringType()),  # *
            StructField("gross_u_cost_security_ccy", DoubleType()),
            StructField("valuation_security_ccy", StringType()),  # *
            StructField("valuation_int_incl_security_ccy", StringType()),  # *
            StructField("accrued_int_security_ccy", StringType()),  # *
            StructField("percent_valintincl", DoubleType()),
            StructField("unrealisedin_percent_securityccy", StringType()),  # *
            StructField("unrealisedin_percent_valuationccy", StringType()),  # *
            StructField("class_code", StringType()),
            StructField("class_code_text", StringType()),
            StructField("reuters_key_code", StringType()),  # *
            StructField("bloomberg_key_code", StringType()),  # *
            StructField("valuation_date", DateType()),
            StructField("next_coupon_payment_date", StringType()),  # DateType()
            StructField("last_coupon_payment_date", StringType()),  # DateType()
            StructField("maturity_date", StringType()),  # DateType()
            StructField("moody_s_rate", StringType()),  # *
            StructField("s_and_prating", StringType()),  # *
            StructField("modified_duration", StringType()),  # *
            StructField("next_call_date", StringType()),  # DateType()
            StructField("valuation_int_incl_chf", DoubleType()),
            StructField("acrrued_in_chf", StringType()),  # Doubletype()
            StructField("fx_rate_secvs_chf", DoubleType()),
            StructField("type_code_sec_vs_chf", StringType()),  # *
            StructField("current_account_key", StringType()),
            StructField("fx_rate_c_c_vs_chf", DoubleType()),
            StructField("type_code_2", StringType()),  # *
            StructField("fx_rate_chf_vs_client_ref", DoubleType()),
            StructField("type_code_3", StringType()),  # *
            StructField("container_no", StringType()),
            StructField("adjustment_factor", StringType()),  # *
            StructField("contract_number", StringType()),  # *
            StructField("unrealised_gross_amount_in_security_currency", DoubleType()),
            StructField("unrealised_gross_amount_in_valuation_currency", DoubleType()),
            StructField("unrealised_net_amount_in_security_currency", DoubleType()),
            StructField("unrealised_net_amount_in_valuation_currency", DoubleType()),
            StructField("new_current_account_key", StringType()),
            StructField("current_account_type_code", StringType()),
            StructField("counterparty", StringType()),  # *
            StructField("custodian_name", StringType()),  # *
            StructField("contract_size", StringType()),  # *
            StructField("ex_custody_position", StringType()),  # *
            StructField("isin_of_underlying_security", StringType()),
            StructField("reference_future", StringType()),
            StructField("market_price_pence", DoubleType()),
        ]),
        "transactions": StructType([
            StructField("portfolio", StringType()),
            StructField("pictet_date", DateType()),
            StructField("transaction", StringType()),
            StructField("pictet_code", StringType()),
            StructField("reversal", StringType()),  # *
            StructField("pictet_id", StringType()),
            StructField("isin", StringType()),
            StructField("telekurs", StringType()),
            StructField("sedol", StringType()),
            StructField("cusip", StringType()),
            StructField("pictet_booking_type", StringType()),
            StructField("booking_date", DateType()),
            StructField("trade_date", DateType()),
            StructField("value_date", DateType()),
            StructField("security_curr", StringType()),
            StructField("cost_price_curr", StringType()),
            StructField("a_c_type", StringType()),
            StructField("a_c_curr", StringType()),
            StructField("contract_nbr", StringType()),  # *
            StructField("texte", StringType()),
            StructField("quantity", StringType()),
            StructField("trade_curr", StringType()),
            StructField("gross_amount_trade_curr", DoubleType()),
            StructField("gross_unit_price", DoubleType()),
            StructField("net_amount_val_curr", DoubleType()),
            StructField("fx_between_trade_and_a_c_curr", DoubleType()),
            StructField("net_amount_a_c_curr", DoubleType()),
            StructField("transaction_description", StringType()),
            StructField("reuters_key_code", StringType()),  # *
            StructField("bloomberg_key_code", StringType()),  # *
            StructField("net_amount_customer_curr", DoubleType()),
            StructField("net_realised_gain_loss", DoubleType()),
            StructField("net_realised_gain_loss_on_market", DoubleType()),
            StructField("net_realised_gain_loss_on_curr", DoubleType()),
            StructField("code_operation_especes", StringType()),  # *
            StructField("brokerage_fees", DoubleType()),
            StructField("foreign_taxs", DoubleType()),
            StructField("execution_fees", StringType()),
            StructField("correspondent_fees", StringType()),
            StructField("db_cr_amount", StringType()),
            StructField("numero_ordre", StringType()),
            StructField("numero_container", StringType()),
            StructField("n_reference_d_origine", StringType()),
            StructField("brokerage_fees_ref_ccy", StringType()),  # DoubleType()
            StructField("execution_fees_ref_ccy", StringType()),  # DoubleType()
            StructField("correspondent_fees_ref_ccy", StringType()),  # DoubleType()
            StructField("foreign_taxs_ref_ccy", StringType()),  # DoubleType()
            StructField("handling_charges", StringType()),  # DoubleType()
            StructField("handling_charges_ref_ccy", StringType()),  # DoubleType()
            StructField("swiss_stamp", StringType()),  # DoubleType()
            StructField("swiss_stamp_ref_ccy", StringType()),  # DoubleType()
            StructField("miscellaneous_fees", StringType()),  # DoubleType()
            StructField("miscellaneous_fees_ref_ccy", StringType()),  # DoubleType()
            StructField("spot_rate", StringType()),
            StructField("adjustment_forward_rate", StringType()),
            StructField("forward_rate", StringType()),
            StructField("ticket_fee", StringType()),
            StructField("subscription_fees", StringType()),
            StructField("text_for_advice", StringType()),
            StructField("vat_amount_trade_curr", StringType()),
            StructField("interest_trade_curr", DoubleType()),
            StructField("solidaritycontributiondetail_included_in_foreigntaxs", DoubleType()),
            StructField("foreignwithholdingtaxdetail_included_in_foreigntaxs", DoubleType()),
            StructField("capitalgaintaxdetail_included_in_foreigntaxs", DoubleType()),
            StructField("text_information", StringType()),
            StructField("unique_trade_identifier", StringType()),
            StructField("fx_between_trade_and_ref_ccy", DoubleType()),
        ]),
    }

    return spark_schema_dict[table_tag]
