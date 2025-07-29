from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema

db_name = "ifls"
data_source = {"morningstar_xml":"asset_morningstar_xml"}


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


class InternationalFeatureColumn:
    def __init__(self):
        self.field_name = 'fund_share_class__international_feature'
        self.target_field_path = ["UKFeature.UKReportingFund.Status.StartDate", "UKFeature.UKReportingFund.Status.Value"]


class PortfolioListsColumn:
    def __init__(self):
        self.field_name = 'fund_share_class__fund__portfolio_list'
        self.target_field_path = ["Portfolio.PortfolioStatistics.BondStatistics.ModifiedDuration", "Portfolio.PortfolioStatistics.BondStatisticsCalculated.BondStatistics.EffectiveDuration", "Portfolio.PortfolioStatistics.BondStatistics.EffectiveDuration", "Portfolio.PortfolioStatistics.BondStatisticsManagerReported.EffectiveDuration", "Portfolio.PortfolioStatistics.BondStatisticsCalculated.BondStatistics.YieldToMaturity", "Portfolio.PortfolioStatistics.BondStatistics.YieldToMaturity", "Portfolio.PortfolioStatistics.BondStatisticsManagerReported.YieldToMaturity", "Portfolio.PortfolioSummary.Date"]


class AnnualReportColumn:
    def __init__(self):
        self.field_name = 'fund_share_class__operation__annual_report'
        self.target_field_path = ["FeeAndExpense.NetExpenseRatio"]


class ColumnClasses:
    def __init__(self):
        self.instantiate = [
            InternationalFeatureColumn(),
            PortfolioListsColumn(),
            AnnualReportColumn()
            
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
            StructField('uk_reporting_fund_status_start_date', StringType()), 
            StructField('uk_reporting_fund_status_value', StringType()),
            StructField('bond_statistics_modified_duration', StringType()), 
            StructField('bond_statistics_calculated_bond_statistics_effective_duration', StringType()), 
            StructField('bond_statistics_effective_duration', StringType()), 
            StructField('bond_statistics_manager_reported_effective_duration', StringType()), 
            StructField('bond_statistics_calculated_bond_statistics_yield_to_maturity', StringType()), 
            StructField('bond_statistics_yield_to_maturity', StringType()), 
            StructField('bond_statistics_manager_reported_yield_to_maturity', StringType()), 
            StructField('portfolio_summary_date', StringType()), 
            StructField('fee_and_expense_net_expense_ratio', StringType()) 
            ])

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
