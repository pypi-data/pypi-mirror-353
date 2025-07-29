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


class KleinwortHambrosTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        self.sep = ","
        self.file_tag = file_tag
        self.date_format = {"*": "dd/MM/yy"}
        self.column_line_index = 0
        self.column_line = []

        if file_tag == "h1":
            self.table_tag = "positions"
        elif file_tag == "t2":
            self.table_tag = "transactions"
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.kleinwort_hambros_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/kleinwort_hambros"
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
            StructField("filedate", DateType()),
            StructField("sghcode", StringType()),
            StructField("sghdesc", StringType()),
            StructField("hldid", StringType()),
            StructField("hldname", StringType()),
            StructField("isin", StringType()),
            StructField("type", StringType()),  # IntegerType()
            StructField("typedesc", StringType()),
            StructField("hldccy", StringType()),
            StructField("quantity", DoubleType()),
            StructField("pricedate", DateType()),
            StructField("price", DoubleType()),
            StructField("mktvalpos", DoubleType()),
            StructField("mktvalgbp", DoubleType()),
        ]),
        "transactions": StructType([
            StructField("filedate", DateType()),
            StructField("sghcode", StringType()),  # LongType()
            StructField("sghdesc", StringType()),
            StructField("account", StringType()),
            StructField("tradedate", DateType()),
            StructField("valdate", DateType()),
            StructField("transcode", StringType()),  # IntegerType()
            StructField("transtype", StringType()),  # IntegerType()
            StructField("transdesc1", StringType()),
            StructField("transdesc2", StringType()),  # LongType()
            StructField("transno", StringType()),
            StructField("trccy", StringType()),
            StructField("amount", DoubleType()),
            StructField("revflag", StringType()),  # IntegerType()
            StructField("sequence", StringType()),
            StructField("balpost", DoubleType()),
            StructField("isin", StringType()),
        ]),
    }

    return spark_schema_dict[table_tag]
