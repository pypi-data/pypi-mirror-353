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


class CitiTable(TablesDynamic):

    def __init__(self, file_tag, data_name, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "yyyyMMdd"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "investments":
            self.table_tag = file_tag
        elif file_tag == "transactions":
            self.table_tag = file_tag

        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.{data_name}_{self.table_tag}"
        s3_endpoint = f"landing/financial_statement/ms-integration/{data_name}"
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
        "investments": StructType([
            StructField("group_name", StringType()),  # *
            StructField("asset_class", StringType()),
            StructField("asset_sub_class", StringType()),
            StructField("industry_sector", StringType()),
            StructField("account_number", StringType()),
            StructField("account_title", StringType()),  # *
            StructField("location", StringType()),
            StructField("custom_account_name", StringType()),  # *
            StructField("account_description", StringType()),
            StructField("account_open_date", DateType()),
            StructField("account_update_date", DateType()),
            StructField("accrued_interest", DoubleType()),
            StructField("rate", DoubleType()),
            StructField("avg_or_unit_cost", DoubleType()),
            StructField("reporting_currency_code", StringType()),
            StructField("nominal_currency_code", StringType()),
            StructField("exchange_rate", DoubleType()),
            StructField("cusip", StringType()),
            StructField("estimated_annual_income", StringType()),  # *
            StructField("market_price", DoubleType()),
            StructField("market_value", DoubleType()),
            StructField("maturity_date", DateType()),
            StructField("principal_income", StringType()),
            StructField("quantity", DoubleType()),
            StructField("security_description", StringType()),
            StructField("security_symbol", StringType()),
            StructField("total_cost_basis", DoubleType()),
            StructField("unrealized_gain_loss", DoubleType()),
            StructField("yield_percent", StringType()),  # *
            StructField("coupon_rate", DoubleType()),
            StructField("exchange_code", StringType()),
            StructField("moody_rating", StringType()),
            StructField("next_coupon_date", DateType()),
            StructField("issue_date", DateType()),
            StructField("price_code", StringType()),
            StructField("price_date", DateType()),
            StructField("price_source", StringType()),
            StructField("s_and_p_rating", StringType()),  # *
            StructField("next_pay_date", StringType()),  # *
            StructField("interest_dividend_at_next_pay_date", StringType()),  # *
            StructField("market_value_in_nominal_currency", DoubleType()),
            StructField("market_price_in_nominal_currency", DoubleType()),
            StructField("total_cost_basis_in_nominal_currency", DoubleType()),
            StructField("avg_or_unit_cost_in_nominal_currency", DoubleType()),
            StructField("unrealized_gain_loss_in_nominal_currency", DoubleType()),
            StructField("accrued_interest_in_nominal_currency", DoubleType()),
            StructField("estimated_annual_income_in_nominal_currency", StringType()),  # *
            StructField("interest_dividend_at_next_pay_date_in_nominal_currency", StringType()),  # *
            StructField("country_of_issuance", StringType()),
            StructField("cash_account_number", StringType()),
            StructField("investment_cash_amount", DoubleType()),
            StructField("investment_cash_in_reporting_currency", DoubleType()),
            StructField("as_of_date", DateType()),
            StructField("interest_at_maturity", DoubleType()),
            StructField("interest_at_maturity_in_nominal_currency", DoubleType()),
            StructField("isin", StringType()),
            StructField("investment", DoubleType()),
            StructField("nav", DoubleType()),
            StructField("asset_value", DoubleType()),
            StructField("capital_commitment", DoubleType()),
            StructField("capital_contribution", DoubleType()),
            StructField("outstanding_commitment", DoubleType()),
            StructField("distributions", DoubleType()),
            StructField("unvalued_contribution", DoubleType()),
            StructField("asset_value_in_nominal_currency", DoubleType()),
            StructField("cash_position_without_accrued_interest", DoubleType()),
            StructField("contract_reference_number", StringType()),
            StructField("cusip_value", StringType()),
            StructField("underlying_security_description", StringType()),  # *
            StructField("receiving_interest_rate", StringType()),  # *
            StructField("pay_interest_rate", StringType()),  # *
        ]),
        "transactions": StructType([
            StructField("group_name", StringType()),  # *
            StructField("account_number", StringType()),
            StructField("custom_account_name", StringType()),  # *
            StructField("account_description", StringType()),
            StructField("account_title", StringType()),  # *
            StructField("location", StringType()),
            StructField("account_open_date", DateType()),
            StructField("account_update_date", DateType()),
            StructField("transaction_date", DateType()),
            StructField("transaction_type", StringType()),
            StructField("transaction_code1", StringType()),
            StructField("transaction_description", StringType()),
            StructField("quantity", DoubleType()),
            StructField("net_settlement_amount", DoubleType()),
            StructField("market_value", DoubleType()),
            StructField("principal_income", DoubleType()),
            StructField("principal", StringType()),
            StructField("interest", StringType()),  # *
            StructField("exchange_rate", DoubleType()),
            StructField("reporting_currency_code", StringType()),
            StructField("nominal_currency_code", StringType()),
            StructField("commission", StringType()),  # DoubleType()
            StructField("contract_date", StringType()),  # *
            StructField("cusip_security_id", StringType()),
            StructField("income", StringType()),  # DoubleType()
            StructField("security_description", StringType()),
            StructField("settle_date", DateType()),
            StructField("security_symbol", StringType()),
            StructField("trade_date", DateType()),
            StructField("settlement_date", DateType()),
            StructField("transaction_id", StringType()),
            StructField("settlement_currency_sell", StringType()),
            StructField("settlement_amount_sell", DoubleType()),
            StructField("settlement_currency_buy", StringType()),
            StructField("settlement_amount_buy", StringType()),  # DoubleType()
            StructField("deal_id", StringType()),
            StructField("purchase_sale_price", DoubleType()),
            StructField("net_settlement_amount_in_nominal_currency", DoubleType()),
            StructField("market_value_in_nominal_currency", StringType()),  # *
            StructField("settlement_cash_account_number", StringType()),
            StructField("settlement_currency", StringType()),
            StructField("value_date", DateType()),
            StructField("transaction_type_code", StringType()),
            StructField("transaction_type_name", StringType()),
            StructField("gross_amount", DoubleType()),
            StructField("brokerage_fees", DoubleType()),
            StructField("withholding_tax", StringType()),  # *
            StructField("withholding_tax_rate", StringType()),  # *
            StructField("withholding_tax1", StringType()),  # *
            StructField("withholding_tax_rate1", StringType()),  # *
            StructField("withholding_tax2", StringType()),  # *
            StructField("withholding_tax_rate2", StringType()),  # *
            StructField("withholding_tax3", DoubleType()),
            StructField("withholding_tax_rate3", DoubleType()),
            StructField("reportable_tax_uk", StringType()),  # *
            StructField("reportable_tax_uk_rate", StringType()),  # *
            StructField("reportable_tax_de", StringType()),  # *
            StructField("reportable_tax_de_rate", StringType()),  # *
            StructField("reportable_tax_at", StringType()),  # *
            StructField("reportable_tax_at_rate", StringType()),  # *
            StructField("reportable_tax_eu", StringType()),  # *
            StructField("reportable_tax_eu_rate", StringType()),  # *
            StructField("withholding_tax_uk", StringType()),  # *
            StructField("withholding_tax_uk_rate", StringType()),  # *
            StructField("withholding_tax_de", StringType()),  # *
            StructField("withholding_tax_de_rate", StringType()),  # *
            StructField("withholding_tax_at", StringType()),  # *
            StructField("withholding_tax_at_rate", StringType()),  # *
            StructField("eu_retention", StringType()),  # *
            StructField("eu_retention_rate", StringType()),  # *
            StructField("withholding_tax_uk1", StringType()),  # *
            StructField("withholding_tax_uk1_rate", StringType()),  # *
            StructField("withholding_tax_de1", StringType()),  # *
            StructField("withholding_tax_de1_rate", StringType()),  # *
            StructField("withholding_tax_at1", StringType()),  # *
            StructField("withholding_tax_at1_rate", StringType()),  # *
            StructField("eu_retention1", StringType()),  # *
            StructField("eu_retention1_rate", StringType()),  # *
            StructField("us_withholding", DoubleType()),
            StructField("us_withholding_rate", DoubleType()),
            StructField("withholding_tax_us", StringType()),  # *
            StructField("withholding_tax_us_rate", StringType()),  # *
            StructField("withholding_tax_us1", StringType()),  # *
            StructField("withholding_tax_us1_rate", StringType()),  # *
            StructField("contract_reference_number", StringType()),
            StructField("recoverable_tax_withheld", DoubleType()),
            StructField("ex_date", DateType()),
            StructField("dividend_per_share", DoubleType()),
            StructField("cusip_value", StringType()),
            StructField("exec_venue", StringType()),
            StructField("exec_date", DateType()),
            StructField("exec_time", StringType()),
            StructField("exec_timezone", StringType()),
            StructField("citibank_commission_amount", DoubleType()),
            StructField("citibank_commission_rate", DoubleType()),
            StructField("fund_manager_commission_amount", DoubleType()),
            StructField("fund_manager_commission_rate", DoubleType()),
            StructField("federal_turnover_tax_amountin_chf", StringType()),  # *
            StructField("federal_turnover_tax_rate", StringType()),  # *
            StructField("transfer_fees_amount", StringType()),  # *
            StructField("transfer_fees_rate", StringType()),  # *
            StructField("corporate_action_fees_amount", StringType()),  # *
            StructField("corporate_action_fees_rate", StringType()),  # *
            StructField("vat_charged_amount", StringType()),  # *
            StructField("vat_charged_rate", StringType()),  # *
            StructField("lodge_withhold_fee_amount", StringType()),  # *
            StructField("lodge_withhold_fee_rate", StringType()),  # *
            StructField("sec_charge_amount", StringType()),  # *
            StructField("sec_charge_rate", StringType()),  # *
            StructField("local_charges_amount", StringType()),  # *
            StructField("local_charges_rate", StringType()),  # *
            StructField("foreign_charges_amount", StringType()),  # *
            StructField("foreign_charges_rate", StringType()),  # *
            StructField("mmi_charges_amount", StringType()),  # *
            StructField("mmi_charges_rate", StringType()),  # *
            StructField("other_charges_amount", StringType()),  # *
            StructField("other_charges_rate", StringType()),  # *
            StructField("clearing_fee_amount", StringType()),  # *
            StructField("clearing_fee_rate", StringType()),  # *
            StructField("exchange_fee_amount", StringType()),  # *
            StructField("exchange_fee_rate", StringType()),  # *
            StructField("accrued_interest_amount", StringType()),  # *
            StructField("accrued_interest_rate", StringType()),  # *
            StructField("fed_turnover_tax_amountin_chf", StringType()),  # *
            StructField("fed_turnover_tax_rate", StringType()),  # *
            StructField("swiss_stock_exchange_fee", StringType()),  # *
            StructField("swiss_stock_exchange_rate", StringType()),  # *
            StructField("trading_fee_amount", StringType()),  # *
            StructField("trading_fee_rate", StringType()),  # *
            StructField("withdrawal_fee_amount", StringType()),  # *
            StructField("withdrawal_fee_rate", StringType()),  # *
            StructField("vat_amount", StringType()),  # *
            StructField("vat_rate", StringType()),  # *
            StructField("sales_tax_amount", StringType()),  # *
            StructField("sales_tax_rate", StringType()),  # *
            StructField("indonesian_vat_amount", StringType()),  # *
            StructField("indonesian_vat_rate", StringType()),  # *
            StructField("ptm_levy_amount", StringType()),  # *
            StructField("ptm_levy_rate", StringType()),  # *
            StructField("ptm_transaction_levy_amount", StringType()),  # *
            StructField("ptm_transaction_levy_rate", StringType()),  # *
            StructField("stamp_duty_amount", StringType()),  # *
            StructField("stamp_duty_rate", StringType()),  # *
            StructField("trading_tariff_amount", StringType()),  # *
            StructField("trading_tariff_rate", StringType()),  # *
            StructField("gst_amount", StringType()),  # *
            StructField("gst_rate", StringType()),  # *
        ])
    }

    return spark_schema_dict[table_tag]
