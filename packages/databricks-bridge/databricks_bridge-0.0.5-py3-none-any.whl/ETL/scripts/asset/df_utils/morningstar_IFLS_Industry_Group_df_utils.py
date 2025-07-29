from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema

db_name = "ifls"
data_source = {"morningstar_xml":"asset_morningstar_industry_group"}


class TablesDynamic(ABC):
    @abstractmethod
    def create_table(self):
        raise NotImplementedError

    @staticmethod
    def get_spark_schema():
        raise NotImplementedError

    @abstractmethod
    def delete_table(self):
        raise NotImplementedError


class PortfolioListsColumn:
    def __init__(self):
        self.field_name = 'fund_share_class__fund__portfolio_list'
        self.target_field_path = [
                                    "Portfolio.PortfolioBreakdown.IndustryGroupBreakdown.BreakdownValue"]


class ColumnClasses:
    def __init__(self):
        self.instantiate = [
            PortfolioListsColumn()
        ]


class MorningstarXMLTable(TablesDynamic):

    def __init__(self):
        self.table_name = f"{db_name}.{data_source['morningstar_xml']}"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        return StructType([
            StructField('isin', StringType()),
            StructField('msid', StringType()), 
            StructField('industry_group_type', StringType()),
            StructField('industry_group_value', StringType()),
            ])

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
