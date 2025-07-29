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


class GoldmanSachsTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = "|"
        self.file_tag = file_tag
        self.date_format = {"*": "ddMMyyyy"}
        self.column_line_index = 1
        self.column_line = []

        if file_tag == "activity":
            self.table_tag = file_tag
        elif file_tag == "holdings":
            self.table_tag = file_tag
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.goldman_sachs_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/goldman_sachs"
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
        "activity": StructType([
            StructField("acct_num", StringType()),  # LongType()
            StructField("instr_iso", StringType()),
            StructField("instr_cusip", StringType()),
            StructField("instr_sedol", StringType()),  # *
            StructField("instr_isin", StringType()),  # *
            StructField("instr_gsnm", StringType()),
            StructField("instr_exchange_cd", StringType()),
            StructField("secdb_reference", StringType()),
            StructField("operation_cd", StringType()),
            StructField("activity_class_cd", StringType()),
            StructField("trade_date", DateType()),
            StructField("settle_date", DateType()),
            StructField("pri_qty", DoubleType()),
            StructField("settle_qty", DoubleType()),
            StructField("settle_iso", StringType()),
            StructField("commission_qty", StringType()),  # *
            StructField("accrued_interest_qty", DoubleType()),
            StructField("pri_instr_price", DoubleType()),
            StructField("underlying_cusip", StringType()),  # *
            StructField("trailer", StringType()),
            StructField("amend_ind", StringType()),
            StructField("trade_ref", StringType()),
            StructField("record_no", StringType()),  # LongType()
            StructField("instr_symbol", StringType()),
            StructField("security_desc", StringType()),
            StructField("acct_mandate_cd", StringType()),  # *
        ]),
        "holdings": StructType([
            StructField("acct_num", StringType()),  # LongType()
            StructField("pos_type_cd", StringType()),
            StructField("instr_iso", StringType()),
            StructField("instr_cusip", StringType()),
            StructField("instr_sedol", StringType()),
            StructField("instr_isin", StringType()),
            StructField("instr_symbol", StringType()),
            StructField("instr_gsnm", StringType()),
            StructField("instr_exchange_cd", StringType()),
            StructField("secdb_reference", StringType()),  # *
            StructField("acct_bs_cur_iso", StringType()),
            StructField("instr_denom_cur_iso", StringType()),
            StructField("port_td_qty", DoubleType()),
            StructField("mv_issue", DoubleType()),
            StructField("mv_base", DoubleType()),
            StructField("market_price_iss", DoubleType()),
            StructField("price_factor", DoubleType()),
            StructField("paydown_factor", DoubleType()),
            StructField("tips_factor", DoubleType()),
            StructField("accrued_amt_iss", DoubleType()),
            StructField("accrued_amt_bs", DoubleType()),
            StructField("port_o_cost_iss", DoubleType()),
            StructField("port_o_cost_bs", DoubleType()),
            StructField("port_a_cost_iss", StringType()),  # *
            StructField("port_a_cost_bs", StringType()),  # *
            StructField("port_c_cost_iss", DoubleType()),
            StructField("port_c_cost_bs", DoubleType()),
            StructField("yld_to_maturity", StringType()),  # *
            StructField("instr_asset_class", StringType()),
            StructField("instr_sub_asset_cd", StringType()),
            StructField("security_desc", StringType()),
            StructField("acct_mandate_cd", StringType()),  # *
        ]),
    }

    return spark_schema_dict[table_tag]
