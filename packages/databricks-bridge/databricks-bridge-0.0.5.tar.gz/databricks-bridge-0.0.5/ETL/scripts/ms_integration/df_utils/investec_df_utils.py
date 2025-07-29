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


class InvestecTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "dd/MM/yyyy"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "trades":
            self.table_tag = file_tag
        elif file_tag == "holdings":
            self.table_tag = file_tag
        elif file_tag == "cash":
            self.table_tag = file_tag
        elif file_tag == "stock":
            self.table_tag = file_tag
        elif file_tag == "valuation":
            self.table_tag = file_tag
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.investec_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/investec"
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
        "trades": StructType([
            StructField("client_ref", StringType()),  # *
            StructField("port_ref", StringType()),  # *
            StructField("bgn_ref", StringType()),  # *
            StructField("bgn_type", StringType()),  # *
            StructField("canc_bgn_ref", StringType()),  # *
            StructField("third_pty_ref", StringType()),  # *
            StructField("buy_sell", StringType()),  # *
            StructField("order_date", StringType()),  # *
            StructField("order_time", StringType()),  # *
            StructField("executed_date", StringType()),  # *
            StructField("executed_time", StringType()),  # *
            StructField("settle_date", StringType()),  # *
            StructField("bgn_conditions", StringType()),  # *
            StructField("isin", StringType()),  # *
            StructField("stock_name", StringType()),  # *
            StructField("stock_desc", StringType()),  # *
            StructField("qty", StringType()),  # *
            StructField("mkt_price", StringType()),  # *
            StructField("mkt_ccy", StringType()),  # *
            StructField("contract_ccy", StringType()),  # *
            StructField("consideration", StringType()),  # *
            StructField("commission", StringType()),  # *
            StructField("ptm_levy", StringType()),  # *
            StructField("stamp_duty", StringType()),  # *
            StructField("other_chgs", StringType()),  # *
            StructField("contract_value", StringType()),  # *
            StructField("order_type", StringType()),  # *
            StructField("trade_venue", StringType()),  # *
            StructField("counterparty", StringType()),  # *
            StructField("acc_int_days", StringType()),  # *
            StructField("acc_int_value", StringType()),  # *
            StructField("real_gain_loss", StringType()),  # *
            StructField("classification", StringType()),  # *
            StructField("class_desc1", StringType()),  # *
            StructField("class_desc2", StringType()),  # *
            StructField("class_desc3", StringType()),  # *
            StructField("class_desc4", StringType()),  # *
            StructField("sec_category", StringType()),  # *
            StructField("cntry_quote", StringType()),  # *
            StructField("exch_quote", StringType()),  # *
            StructField("sedol", StringType()),  # *
            StructField("is_cash", StringType()),  # *
            StructField("issue_name", StringType()),  # *
            StructField("security_desc", StringType()),  # *
            StructField("exch_rate", StringType()),  # *
            StructField("mkt_rep_ccy", StringType()),  # *
            StructField("clt_rep_ccy", StringType()),  # *
            StructField("tax_rep_ccy", StringType()),  # *
            StructField("mkt_rep_book_cost", StringType()),  # *
            StructField("clt_rep_book_cost", StringType()),  # *
            StructField("tax_rep_book_cost", StringType()),  # *
        ]),
        "holdings": StructType([
            StructField("client_ref", StringType()),
            StructField("port_ref", StringType()),
            StructField("value", DoubleType()),
            StructField("valuation_date", DateType()),
            StructField("port_ccy", StringType()),
            StructField("sedol", StringType()),
            StructField("isin", StringType()),
            StructField("stock_name", StringType()),
            StructField("stock_desc", StringType()),
            StructField("quantity", DoubleType()),
            StructField("mkt_price", DoubleType()),
            StructField("mkt_ccy", StringType()),
            StructField("port_price", DoubleType()),
            StructField("price_date", DateType()),
            StructField("book_cost", DoubleType()),
            StructField("port_value", DoubleType()),
            StructField("acc_int_days", StringType()),  # IntegerType()
            StructField("acc_int_value", StringType()),  # IntegerType()
            StructField("income", DoubleType()),
            StructField("yield", DoubleType()),
            StructField("custody_qty", DoubleType()),
            StructField("sec_category", StringType()),
            StructField("cntry_quote", StringType()),
            StructField("exch_quote", StringType()),
            StructField("classification", StringType()),  # LongType()
            StructField("class_desc1", StringType()),
            StructField("class_desc2", StringType()),
            StructField("class_desc3", StringType()),
            StructField("class_desc4", StringType()),
            StructField("issue_name", StringType()),
            StructField("security_desc", StringType()),
            StructField("mkt_rep_ccy", StringType()),  # *
            StructField("mkt_rep_book_cost", StringType()),  # *
            StructField("tax_rep_ccy", StringType()),  # *
            StructField("tax_rep_book_cost", StringType()),  # *
        ]),
        "cash": StructType([
            StructField("client_ref", StringType()),
            StructField("port_ref", StringType()),
            StructField("transaction_ref", StringType()),
            StructField("cash_type", StringType()),
            StructField("transaction_type", StringType()),
            StructField("ca_transaction_type", StringType()),  # *
            StructField("movement_date", DateType()),
            StructField("transaction_ldg", StringType()),
            StructField("transaction_narr", StringType()),
            StructField("currency", StringType()),
            StructField("value", DoubleType()),
            StructField("balance", StringType()),  # DoubleType()
            StructField("sec_category", StringType()),  # *
            StructField("cntry_quote", StringType()),  # *
            StructField("exch_quote", StringType()),  # *
            StructField("ledger", StringType()),
            StructField("isin", StringType()),  # *
            StructField("stock_name", StringType()),  # *
            StructField("stock_desc", StringType()),  # *
            StructField("classification", StringType()),  # LongType()
            StructField("class_desc1", StringType()),  # *
            StructField("class_desc2", StringType()),  # *
            StructField("class_desc3", StringType()),  # *
            StructField("class_desc4", StringType()),  # *
            StructField("transaction_date", StringType()),  # *
        ]),
        "stock": StructType([
            StructField("client_ref", StringType()),  # *
            StructField("port_ref", StringType()),  # *
            StructField("transact_ref", StringType()),  # *
            StructField("stock_type", StringType()),  # *
            StructField("transact_type", StringType()),  # *
            StructField("ca_type", StringType()),  # *
            StructField("isin", StringType()),  # *
            StructField("stock_name", StringType()),  # *
            StructField("stock_desc", StringType()),  # *
            StructField("port_mvmt_date", StringType()),  # *
            StructField("port_qty", StringType()),  # *
            StructField("custody_mvmt_date", StringType()),  # *
            StructField("custody_qty", StringType()),  # *
            StructField("sec_category", StringType()),  # *
            StructField("cntry_quote", StringType()),  # *
            StructField("exch_quote", StringType()),  # *
            StructField("classification", StringType()),  # *
            StructField("class_desc1", StringType()),  # *
            StructField("class_desc2", StringType()),  # *
            StructField("class_desc3", StringType()),  # *
            StructField("class_desc4", StringType()),  # *
            StructField("sedol", StringType()),  # *
            StructField("is_cash", StringType()),  # *
            StructField("issue_name", StringType()),  # *
            StructField("security_desc", StringType()),  # *
            StructField("transaction_bookcost", StringType()),  # *
            StructField("portfolio_currency", StringType()),  # *
            StructField("before_bookcost", StringType()),  # *
            StructField("after_bookcost", StringType()),  # *
        ]),
        "valuation": StructType([
            StructField("client_ref", StringType()),
            StructField("port_ref", StringType()),
            StructField("bgn_ref", StringType()),  # *
            StructField("bgn_type", StringType()),  # *
            StructField("canc_bgn_ref", StringType()),  # *
            StructField("third_pty_ref", StringType()),  # *
            StructField("buy_sell", StringType()),  # *
            StructField("order_date", StringType()),  # *
            StructField("order_time", StringType()),  # *
            StructField("executed_date", StringType()),  # *
            StructField("executed_time", StringType()),  # *
            StructField("settle_date", StringType()),  # *
            StructField("bgn_conditions", StringType()),  # *
            StructField("isin", StringType()),
            StructField("stock_name", StringType()),
            StructField("stock_desc", StringType()),
            StructField("qty", StringType()),  # *
            StructField("mkt_price", DoubleType()),
            StructField("mkt_ccy", StringType()),
            StructField("contract_ccy", StringType()),  # *
            StructField("consideration", StringType()),  # *
            StructField("commission", StringType()),  # *
            StructField("ptm_levy", StringType()),  # *
            StructField("stamp_duty", StringType()),  # *
            StructField("other_chgs", StringType()),  # *
            StructField("contract_value", StringType()),  # *
            StructField("order_type", StringType()),  # *
            StructField("trade_venue", StringType()),  # *
            StructField("counterparty", StringType()),  # *
            StructField("acc_int_days", StringType()),  # IntegerType()
            StructField("acc_int_value", StringType()),  # IntegerType()
            StructField("real_gain_loss", StringType()),  # *
            StructField("classification", StringType()),  # LongType()
            StructField("class_desc1", StringType()),
            StructField("class_desc2", StringType()),
            StructField("class_desc3", StringType()),
            StructField("class_desc4", StringType()),
            StructField("sec_category", StringType()),
            StructField("cntry_quote", StringType()),
            StructField("exch_quote", StringType()),
            StructField("sedol", StringType()),
            StructField("is_cash", StringType()),  # *
            StructField("issue_name", StringType()),
            StructField("security_desc", StringType()),
            StructField("exch_rate", StringType()),  # *
            StructField("mkt_rep_ccy", StringType()),  # *
            StructField("clt_rep_ccy", StringType()),  # *
            StructField("tax_rep_ccy", StringType()),  # *
            StructField("mkt_rep_book_cost", StringType()),  # *
            StructField("clt_rep_book_cost", StringType()),  # *
            StructField("tax_rep_book_cost", StringType()),  # *
        ]),
    }

    return spark_schema_dict[table_tag]
