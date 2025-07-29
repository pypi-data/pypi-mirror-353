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


class MorganStanleyTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "yyyy-MM-dd"}
        self.column_line_index = 3
        self.column_line = []

        if file_tag == "posit":
            self.table_tag = "positions"
        elif file_tag == "trans":
            self.table_tag = "transactions"
            self.date_format = {"tran_date": "yyyy-MM-dd", "settle_date": "yyyy-MM-dd",
                                "trade_date": "MMddyyyy", "trade_date_1": "MMddyyyy"}
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.morgan_stanley_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/morgan_stanley"
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
            StructField("routing_code", StringType()),
            StructField("account", StringType()),  # LongType()
            StructField("cusip", StringType()),
            StructField("security_description", StringType()),
            StructField("quantity", DoubleType()),
            StructField("market_base", DoubleType()),
            StructField("market_local", DoubleType()),
            StructField("coupon_rate", DoubleType()),
            StructField("issue_date", StringType()),  # *
            StructField("maturity_date", StringType()),  # *
            StructField("original_face", DoubleType()),
            StructField("factor", DoubleType()),
            StructField("currency", StringType()),
            StructField("symbol", StringType()),
            StructField("total_cost", DoubleType()),
            StructField("exchange", StringType()),  # IntegerType()
            StructField("account_type", StringType()),  # IntegerType()
            StructField("security_code", StringType()),
            StructField("security_no", StringType()),
            StructField("sedol", StringType()),  # LongType()
            StructField("isin", StringType()),
            StructField("settlement_quantity", DoubleType()),
            StructField("market_base_sd", DoubleType()),
            StructField("product_id", StringType()),
            StructField("restricted_sec_flag", StringType()),  # *
            StructField("restricted_quantity", DoubleType()),
            StructField("long_short_indicator", StringType()),
            StructField("blank", StringType()),  # *
            StructField("quantity_1", DoubleType()),
            StructField("symbol_cusip", StringType()),
            StructField("position_as_of_date", DateType()),
            StructField("alternate_security_indicator", StringType()),  # *
            StructField("wash_sales_indicator", StringType()),  # *
            StructField("blank2", StringType()),  # LongType()
        ]),
        "transactions": StructType([
            StructField("routing_code", StringType()),
            StructField("account", StringType()),  # LongType()
            StructField("cusip", StringType()),
            StructField("security_description", StringType()),
            StructField("tran_code", StringType()),
            StructField("tran_date", DateType()),
            StructField("trade_date", StringType()),  # *
            StructField("settle_date", DateType()),
            StructField("quantity", DoubleType()),
            StructField("price", DoubleType()),
            StructField("accrued_interest", DoubleType()),
            StructField("other_fee_base", DoubleType()),
            StructField("other_fee_local", DoubleType()),
            StructField("comm_base", DoubleType()),
            StructField("comm_local", DoubleType()),
            StructField("total_amount", DoubleType()),
            StructField("broker", StringType()),
            StructField("fx_rate", DoubleType()),
            StructField("secondary_fee_base", DoubleType()),
            StructField("secondary_fee_local", DoubleType()),
            StructField("original_face", DoubleType()),
            StructField("factor", DoubleType()),
            StructField("coupon", DoubleType()),
            StructField("issue_date", StringType()),  # *
            StructField("maturity_date", StringType()),  # *
            StructField("current_order", StringType()),  # *
            StructField("previous_order", StringType()),  # *
            StructField("cancel_indicator", StringType()),  # *
            StructField("buy_sell_indicator", StringType()),
            StructField("symbol", StringType()),
            StructField("exchange", StringType()),  # DoubleType()
            StructField("security_code", StringType()),
            StructField("security_no", StringType()),
            StructField("postage_amount", DoubleType()),
            StructField("foreign_tax", DoubleType()),
            StructField("fc_number", StringType()),
            StructField("broker_code_1_4", StringType()),  # *
            StructField("broker_code_5_6", StringType()),  # *
            StructField("broker_code_7", StringType()),  # *
            StructField("sedol", StringType()),  # LongType()
            StructField("isin", StringType()),
            StructField("principal", DoubleType()),
            StructField("confirm_trailer", StringType()),  # *
            StructField("filler", StringType()),  # *
            StructField("vsp_vode", StringType()),  # *
            StructField("alternate_transaction_code", StringType()),
            StructField("trade_date_1", DateType()),
            StructField("sb_alpha_tran_code", StringType()),
            StructField("sb_source_destination", StringType()),
            StructField("solicited_or_nonsolicited", StringType()),
            StructField("sub_category_code", StringType()),
            StructField("blank", StringType()),  # *
            StructField("new_symbol_field", StringType()),
            StructField("new_security_type", StringType()),
            StructField("vsp_date_2", StringType()),  # *
            StructField("vsp_price_2", StringType()),  # *
            StructField("vsp_quantity_2", StringType()),  # *
            StructField("alternate_security_indicator", StringType()),
            StructField("blank2", StringType()),  # *
        ]),
    }

    return spark_schema_dict[table_tag]
