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


class JuliusBaerTable(TablesDynamic):

    def __init__(self, file_tag, db_name):
        # self.sep = "\t"
        self.file_tag = file_tag
        self.date_format = {"*": "yyyyMMdd"}  # pos: col4
        self.column_line_index = 0

        if file_tag == "pos":
            self.table_tag = "positions"
            self.sep = "\t"
            self.column_line = [self.sep.join([f"col_{i}" for i in range(125)])]
        elif file_tag == "bew":
            self.table_tag = "transactions"
            self.sep = ";"
            self.column_line = [self.sep.join([f"col_{i}" for i in range(109)])]
            # self.date_format = {"col25": "yyyyMMdd", "col26": "yyyyMMdd", "col41": "yyyyMMdd", "col48": "yyyyMMdd",
            #                     "col56": "yyyyMMdd",
            #
            #                     "col97": "yyyyMMddHHmms"}
        else:
            self.table_tag = ""

        self.table_name = f"{db_name}.julius_baer_{self.table_tag}"
        s3_endpoint = "landing/financial_statement/ms-integration/julius_baer"
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
            StructField("col0", StringType()),  # *
            StructField("col1", StringType()),  # LongType()
            StructField("col2", StringType()),  # LongType()
            StructField("col3", StringType()),
            StructField("col4", DateType()),
            StructField("col5", StringType()),  # LongType()
            StructField("col6", StringType()),  # LongType()
            StructField("col7", StringType()),  # *
            StructField("col8", StringType()),  # LongType()
            StructField("col9", StringType()),  # *
            StructField("col10", StringType()),  # *
            StructField("col11", StringType()),  # LongType()
            StructField("col12", StringType()),  # *
            StructField("col13", DoubleType()),
            StructField("col14", StringType()),  # LongType()
            StructField("col15", StringType()),  # LongType()
            StructField("col16", StringType()),  # LongType()
            StructField("col17", StringType()),  # LongType()
            StructField("col18", StringType()),  # LongType()
            StructField("col19", DoubleType()),
            StructField("col20", DoubleType()),
            StructField("col21", StringType()),  # LongType()
            StructField("col22", StringType()),  # LongType()
            StructField("col23", StringType()),  # *
            StructField("col24", StringType()),  # *
            StructField("col25", StringType()),  # LongType()
            StructField("col26", StringType()),  # *
            StructField("col27", StringType()),  # *
            StructField("col28", StringType()),  # *
            StructField("col29", StringType()),  # *
            StructField("col30", DateType()),
            StructField("col31", StringType()),  # *
            StructField("col32", StringType()),  # *
            StructField("col33", StringType()),  # *
            StructField("col34", StringType()),  # *
            StructField("col35", DateType()),
            StructField("col36", StringType()),  # *
            StructField("col37", StringType()),  # *
            StructField("col38", StringType()),  # *
            StructField("col39", StringType()),  # *
            StructField("col40", DateType()),
            StructField("col41", StringType()),  # *
            StructField("col42", StringType()),  # *
            StructField("col43", StringType()),  # *
            StructField("col44", StringType()),  # *
            StructField("col45", DateType()),  # LongType()
            StructField("col46", StringType()),  # *
            StructField("col47", StringType()),  # *
            StructField("col48", StringType()),  # *
            StructField("col49", StringType()),  # *
            StructField("col50", StringType()),  # LongType()
            StructField("col51", StringType()),  # *
            StructField("col52", StringType()),  # *
            StructField("col53", StringType()),  # *
            StructField("col54", StringType()),  # *
            StructField("col55", StringType()),  # LongType()
            StructField("col56", StringType()),  # *
            StructField("col57", StringType()),  # *
            StructField("col58", StringType()),  # *
            StructField("col59", StringType()),  # *
            StructField("col60", StringType()),  # LongType()
            StructField("col61", StringType()),  # *
            StructField("col62", StringType()),  # *
            StructField("col63", StringType()),  # *
            StructField("col64", StringType()),  # *
            StructField("col65", StringType()),  # LongType()
            StructField("col66", StringType()),  # *
            StructField("col67", StringType()),  # *
            StructField("col68", StringType()),  # *
            StructField("col69", StringType()),  # *
            StructField("col70", StringType()),  # LongType()
            StructField("col71", StringType()),  # *
            StructField("col72", StringType()),  # *
            StructField("col73", StringType()),  # LongType()
            StructField("col74", StringType()),  # IntegerType()
            StructField("col75", DoubleType()),
            StructField("col76", DoubleType()),
            StructField("col77", DateType()),  # LongType()
            StructField("col78", StringType()),  # LongType()
            StructField("col79", StringType()),  # *
            StructField("col80", StringType()),  # IntegerType()
            StructField("col81", StringType()),  # LongType()
            StructField("col82", StringType()),  # *
            StructField("col83", StringType()),  # *
            StructField("col84", StringType()),  # *
            StructField("col85", StringType()),  # LongType()
            StructField("col86", StringType()),
            StructField("col87", StringType()),
            StructField("col88", StringType()),
            StructField("col89", DoubleType()),
            StructField("col90", StringType()),  # *
            StructField("col91", DoubleType()),
            StructField("col92", StringType()),  # LongType()
            StructField("col93", DoubleType()),
            StructField("col94", DoubleType()),
            StructField("col95", DoubleType()),
            StructField("col96", DoubleType()),
            StructField("col97", StringType()),
            StructField("col98", StringType()),  # IntegerType()
            StructField("col99", StringType()),
            StructField("col100", StringType()),  # LongType()
            StructField("col101", StringType()),  # *
            StructField("col102", StringType()),  # IntegerType()
            StructField("col103", StringType()),  # *
            StructField("col104", StringType()),  # *
            StructField("col105", StringType()),  # *
            StructField("col106", StringType()),  # LongType()
            StructField("col107", StringType()),  # *
            StructField("col108", StringType()),  # *
            StructField("col109", StringType()),  # *
            StructField("col110", StringType()),  # *
            StructField("col111", StringType()),  # *
            StructField("col112", StringType()),  # *
            StructField("col113", StringType()),  # *
            StructField("col114", StringType()),  # *
            StructField("col115", StringType()),  # *
            StructField("col116", StringType()),  # *
            StructField("col117", StringType()),  # *
            StructField("col118", DoubleType()),
            StructField("col119", StringType()),  # *
            StructField("col120", StringType()),  # *
            StructField("col121", StringType()),  # *
            StructField("col122", StringType()),  # *
            StructField("col123", StringType()),  # *
            StructField("col124", StringType()),  # *
        ]),
        "transactions": StructType([
            StructField("col0", StringType()),
            StructField("col1", StringType()),  # LongType()
            StructField("col2", StringType()),  # LongType()
            StructField("col3", StringType()),  # LongType()
            StructField("col4", StringType()),  # LongType()
            StructField("col5", StringType()),  # LongType()
            StructField("col6", StringType()),  # IntegerType()
            StructField("col7", StringType()),
            StructField("col8", StringType()),
            StructField("col9", StringType()),
            StructField("col10", StringType()),
            StructField("col11", StringType()),  # *
            StructField("col12", StringType()),  # *
            StructField("col13", DoubleType()),
            StructField("col14", DoubleType()),
            StructField("col15", StringType()),
            StructField("col16", StringType()),
            StructField("col17", StringType()),  # IntegerType()
            StructField("col18", DoubleType()),
            StructField("col19", StringType()),
            StructField("col20", StringType()),  # IntegerType()
            StructField("col21", DoubleType()),
            StructField("col22", DoubleType()),
            StructField("col23", StringType()),  # LongType()
            StructField("col24", StringType()),
            StructField("col25", DateType()),
            StructField("col26", DateType()),
            StructField("col27", StringType()),
            StructField("col28", StringType()),
            StructField("col29", StringType()),
            StructField("col30", DoubleType()),
            StructField("col31", StringType()),  # *
            StructField("col32", DoubleType()),
            StructField("col33", DoubleType()),
            StructField("col34", StringType()),  # *
            StructField("col35", StringType()),  # *
            StructField("col36", StringType()),
            StructField("col37", StringType()),  # *
            StructField("col38", DoubleType()),
            StructField("col39", StringType()),  # IntegerType()
            StructField("col40", StringType()),  # LongType()
            StructField("col41", DateType()),
            StructField("col42", StringType()),  # *
            StructField("col43", StringType()),  # *
            StructField("col44", StringType()),  # *
            StructField("col45", StringType()),  # *
            StructField("col46", StringType()),  # *
            StructField("col47", StringType()),
            StructField("col48", DateType()),
            StructField("col49", StringType()),  # *
            StructField("col50", StringType()),  # *
            StructField("col51", StringType()),  # *
            StructField("col52", StringType()),  # LongType()
            StructField("col53", StringType()),
            StructField("col54", DoubleType()),
            StructField("col55", StringType()),
            StructField("col56", DateType()),
            StructField("col57", StringType()),
            StructField("col58", DoubleType()),
            StructField("col59", StringType()),  # IntegerType()
            StructField("col60", DoubleType()),
            StructField("col61", StringType()),  # *
            StructField("col62", StringType()),  # *
            StructField("col63", StringType()),  # *
            StructField("col64", StringType()),  # *
            StructField("col65", StringType()),  # *
            StructField("col66", StringType()),  # *
            StructField("col67", StringType()),  # *
            StructField("col68", StringType()),  # *
            StructField("col69", StringType()),  # *
            StructField("col70", StringType()),  # *
            StructField("col71", StringType()),  # *
            StructField("col72", StringType()),  # *
            StructField("col73", StringType()),  # *
            StructField("col74", StringType()),  # *
            StructField("col75", StringType()),  # *
            StructField("col76", StringType()),  # *
            StructField("col77", StringType()),
            StructField("col78", StringType()),
            StructField("col79", StringType()),
            StructField("col80", DoubleType()),
            StructField("col81", DoubleType()),
            StructField("col82", StringType()),  # *
            StructField("col83", StringType()),  # *
            StructField("col84", StringType()),  # *
            StructField("col85", StringType()),  # *
            StructField("col86", StringType()),  # *
            StructField("col87", StringType()),  # *
            StructField("col88", StringType()),  # *
            StructField("col89", StringType()),  # *
            StructField("col90", StringType()),  # *
            StructField("col91", StringType()),  # *
            StructField("col92", StringType()),  # *
            StructField("col93", StringType()),  # *
            StructField("col94", StringType()),  # *
            StructField("col95", StringType()),
            StructField("col96", StringType()),  # *
            StructField("col97", StringType()),
            StructField("col98", StringType()),  # *
            StructField("col99", StringType()),  # *
            StructField("col100", StringType()),  # *
            StructField("col101", StringType()),
            StructField("col102", StringType()),  # *
            StructField("col103", StringType()),  # *
            StructField("col104", StringType()),  # *
            StructField("col105", StringType()),
            StructField("col106", StringType()),  # *
            StructField("col107", StringType()),
            StructField("col108", StringType()),  # *
        ]),
    }

    return spark_schema_dict[table_tag]
