from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns
from ETL.commons.ease_of_use_fcns import get_checkpoint_dir

db_name = "cleansed"
data_source = "ms_asset"
possible_prefixes = ["created", "deleted", "refreshed", "updated"]
unappendable_parent_keys = ["rows", "collection", "history", "rowInfo", "transactions", "values", "source"]
checkpoint_dir = get_checkpoint_dir("ms_asset")


def get_data_lineage(table_name):
    return {
        'target_type': "lakehouse",
        'target_endpoint': table_name,
        'src0_type': "s3",
        'src0_endpoint': "landing/asset/ms_asset",
        'etl_script_path': "ETL/scripts/ms_asset/all_ms_asset.py",
        'src1_type': "service",
        'src1_endpoint': "ms-datalake-connector",
        'src1_script_path': "src/main/kotlin/com/ytree/msdatalakeconnector/adapter/driver/kafka/listener/MsAssetEventListener.kt",
        'src2_type': "kafka",
        'src2_endpoint': "MS_ASSET_EVENT_TOPIC",
        'src2_script_path': ""
    }


class TablesDynamic(ABC):
    @abstractmethod
    def create_table(self):
        raise NotImplementedError

    @staticmethod
    def get_spark_schema():
        raise NotImplementedError

    @staticmethod
    def notes():
        raise NotImplementedError

    @abstractmethod
    def delete_table(self):
        raise NotImplementedError


class PublicTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "public"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {"rowInfo": {
            "createdAt": None, "createdBy": None, "updatedAt": None, "updatedBy": None, "deletedAt": None,
            "deletedBy": None, "changes_source": None,
        }}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("isin", StringType()),
            StructField("sedol", StringType()),
            StructField("cusip", StringType()),
            StructField("preqin_id", StringType()),
            StructField("status_type", StringType()),
            StructField("is_benchmark", BooleanType()),
            StructField("external_id", StringType()),
            StructField("managed_by_y_tree", BooleanType()),
            StructField("can_delete", BooleanType()),
            StructField("primary_share_class_isin", StringType()),
            StructField("fund_type", StringType()),
            StructField("is_special_arrangement", BooleanType()),
            StructField("fund_strategy", StringType()),
            StructField("exchange_traded_share", BooleanType()),
#             StructField("row_info", StringType()),
            StructField("changes_source", StringType()),
            StructField("created_at", TimestampType()),
            StructField("created_by", StringType()),
            StructField("updated_at", TimestampType()),
            StructField("updated_by", StringType()),
            StructField("deleted_at", TimestampType()),
            StructField("deleted_by", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class PrivateTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "private"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {"rowInfo": {
            "createdAt": None, "createdBy": None, "updatedAt": None, "updatedBy": None, "deletedAt": None,
            "deletedBy": None, "changes_source": None,
        }}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField('isin', StringType()),
            StructField('client_id', StringType()),
            StructField('status', StringType()),
            StructField('created_at', TimestampType()),
            StructField('created_by', StringType()),
            StructField('updated_at', TimestampType()),
            StructField('updated_by', StringType()),
            StructField("deleted_at", TimestampType()),
            StructField("deleted_by", StringType()),
            StructField("changes_source", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class PersonalTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "personal"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("isin", StringType()),
            StructField("purchase_date", DateType()),
            StructField("purchase_price", DoubleType()),
            StructField("estimated_current_value", DoubleType()),
            StructField("other_related_costs", DoubleType()),
            StructField("insurance_expiry_date", DateType()),
            StructField("insurance_provider", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class PropertyTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "property"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField('isin', StringType()),
            StructField('house_number', StringType()),
            StructField('address', StringType()),
            StructField('country', StringType()),
            StructField('postcode', StringType()),
            StructField('stamp_duty', DoubleType()),
            StructField('renovation_cost', DoubleType()),
            StructField('gas_safety_expiry_date', DateType()),
            StructField('gas_safety_provider', StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class LoanTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "loan"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("isin", StringType()),
            StructField("borrower_name", StringType()),
            StructField("amount", DoubleType()),
            StructField("rate", DoubleType()),
            StructField("start_date", DateType()),
            StructField("end_date", DateType()),
            StructField("payment_day", IntegerType()),
            StructField("frequency", IntegerType()),
            StructField("payment_type", IntegerType()),
            StructField("security", DoubleType()),
            StructField("facilitator", StringType()),
            StructField("notes", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class InvestmentTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "investment"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField('isin', StringType()),
            StructField('start_date', DateType()),
            StructField('tax_treatment', StringType()),
            StructField('price', DoubleType()),
            StructField('number_of_shares', DoubleType()),
            StructField('share_class', StringType()),
            StructField('notes', StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class ClassTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "class"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("isin", StringType()),
            StructField("cash", DoubleType()),
            StructField("dm_government_bonds", DoubleType()),
            StructField("inflation_linked_bonds", DoubleType()),
            StructField("emerging_market_bonds", DoubleType()),
            StructField("investment_grade_corporate_bonds", DoubleType()),
            StructField("diversified_fixed_income", DoubleType()),
            StructField("high_yield_bonds", DoubleType()),
            StructField("public_equities", DoubleType()),
            StructField("preferred_public_equities", DoubleType()),
            StructField("hedge_funds", DoubleType()),
            StructField("broad_commodities", DoubleType()),
            StructField("gold", DoubleType()),
            StructField("investment_property", DoubleType()),
            StructField("primary_residence", DoubleType()),
            StructField("residential_property", DoubleType()),
            StructField("private_property_fund", DoubleType()),
            StructField("private_equity_fund_buyout", DoubleType()),
            StructField("private_equity_fund_venture_capital", DoubleType()),
            StructField("private_debt_fund", DoubleType()),
            StructField("private_company_investment", DoubleType()),
            StructField("private_loan", DoubleType()),
            StructField("car", DoubleType()),
            StructField("yacht", DoubleType()),
            StructField("collectable_wine_and_spirits", DoubleType()),
            StructField("art", DoubleType()),
            StructField("jewellery_and_watches", DoubleType()),
            StructField("other_collectables", DoubleType()),
            StructField("diversified_strategies", DoubleType()),
            StructField("other", DoubleType()),
            StructField("reit", DoubleType()),
            StructField("unknown", DoubleType()),
            StructField("company_option", DoubleType()),
            StructField("derivative", DoubleType()),
            StructField("is_asset_class_changed", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class CollectionCurrencyExposureTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "collection_currency_exposure"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {"collection": [{"conversion_rate": None, "currency_code": None}]}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField('isin', StringType()),
            StructField('currency_code', StringType()),
            StructField('conversion_rate', DoubleType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class FeeTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "fee"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("isin", StringType()),
            StructField("management", DoubleType()),
            StructField("entry", DoubleType()),
            StructField("exit", DoubleType()),
            StructField("total_expense_ratio", DoubleType()),
            StructField("performance", DoubleType()),
            StructField("projected_actual_performance", DoubleType()),
            StructField("administration", DoubleType()),
            StructField("spread_bid_ask", DoubleType()),
            StructField("ter_adjustment", DoubleType()),
            StructField("notes", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class FixedIncomeTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "fixed_income"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField('isin', StringType()),
            StructField('yield_to_maturity', DoubleType()),
            StructField('duration', DoubleType()),
            StructField('maturity_date', DateType()),
            StructField('average_credit_rating', StringType()),
            StructField('credit_ratings', StringType()),
            StructField('credit_ratings_breakdown', StringType()), #* couldnt find a file with a non-empty creditRating field
            StructField('credit_ratings_breakdown_value', DoubleType()), #* couldnt find a file with a non-empty creditRating field
            StructField('coupon_frequency', DoubleType()),
            StructField('interest_rate', DoubleType()),
            StructField('par_value', DoubleType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """
        credit_ratings:
            This field should come with a dictionary values that gets normalized into the following fields:
                'credit_ratings_breakdown' and 'credit_ratings_breakdown_value'
            It sometimes comes with null values instead of filled or empty dictionary.
            This causes it to trigger a warning that says the field is missing from schema but exists in data file
        """

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class RiskExposureTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "risk_exposure"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("isin", StringType()),
            StructField("total", DoubleType()),
            StructField("stocks", DoubleType()),
            StructField("interest_rates", DoubleType()),
            StructField("inflation", DoubleType()),
            StructField("credit", DoubleType()),
            StructField("asset_var", DoubleType()),
            StructField("risk_var", DoubleType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class BetaHistoryExposureTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "beta_history_exposure"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {"history": [{
            "isApproved": None, "date": None, "effectiveDate": None, "exposures": {
                "PROPERTY": None, "BROAD_COMMODITIES": None, "HIGH_YIELD_CREDIT": None, "EMERGING_MARKET_STOCKS": None,
                "DEVELOPED_MARKET_STOCKS": None, "GOVERNMENT_BONDS_10_YEAR": None, "INFLATION_LINKED_BONDS_10_YEAR": None
            }
        }]}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField('isin', StringType()),
            StructField('type', StringType()),
            StructField('reference_asset', StringType()),
            StructField('is_approved', BooleanType()),
            StructField('date', DateType()),
            StructField('effective_date', DateType()),
            StructField('exposures_broad_commodities', DoubleType()),
            StructField('exposures_developed_market_stocks', DoubleType()),
            StructField('exposures_emerging_market_stocks', DoubleType()),
            StructField('exposures_high_yield_credit', DoubleType()),
            StructField('exposures_property', DoubleType()),
            StructField('exposures_government_bonds_10_year', DoubleType()),
            StructField('exposures_inflation_linked_bonds_10_year', DoubleType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class TradingCycleTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "trading_cycle"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("isin", StringType()),
            StructField("notification_window_start", IntegerType()),
            StructField("notification_start_time", StringType()),
            StructField("notification_window_end", IntegerType()),
            StructField("notification_cutoff_time", StringType()),
            StructField("settlement", IntegerType()),
            StructField("settlement_type", StringType()),
            StructField("trading_frequency", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class MarketValuesTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "market_values"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {"prices": [{"date": None, "value": None}]}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField('isin', StringType()),
            StructField('prices_date', DateType()),
            StructField('prices_value', DoubleType()),
            StructField('is_last_price_changed', StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class TotalReturnIndexesTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "total_return_indexes"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {"tri": [{"date": None, "value": None}]}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("isin", StringType()),
#             StructField("tri", StringType()),
            StructField("tri_date", DateType()),
            StructField("tri_value", DoubleType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class PrivateEquityTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "private_equity"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {"rowInfo": {
            "createdAt": None, "createdBy": None, "updatedAt": None, "updatedBy": None, "deletedAt": None,
            "deletedBy": None, "changes_source": None,
        }}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField('asset_id', StringType()),
            StructField('internal_rate_return', DoubleType()),
            StructField('fund_vintage', IntegerType()),
            StructField('launch_date', DateType()),
            StructField('fund_size', DoubleType()),
            StructField('multiple', DoubleType()),
            StructField('investment_term', IntegerType()),
            StructField('created_at', TimestampType()),
            StructField('created_by', StringType()),
            StructField('updated_at', TimestampType()),
            StructField('updated_by', StringType()),
            StructField('changes_source', StringType()),
            StructField('deleted_at', StringType()),
            StructField('deleted_by', StringType()),
            StructField('preqin_id', StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class PrivateEquityTransactionsTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "private_equity_transactions"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {"transactions": [{
            "id": None, "date": None, "amount": None, "amount_in_asset_currency": None, "currency": None,
            "type": None, "description": None,
        }]}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("asset_id", StringType()),
            StructField("id", LongType()),
            StructField("date", DateType()),
            StructField("amount", DoubleType()),
            StructField("amount_in_asset_currency", DoubleType()),
            StructField("currency", IntegerType()),
            StructField("type", StringType()),
            StructField("description", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class PrivateEquityProjectedCapitalCallsTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "private_equity_projected_capital_calls"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {"rowInfo": {
            "createdAt": None, "createdBy": None, "updatedAt": None, "updatedBy": None, "deletedAt": None,
            "deletedBy": None, "changes_source": None,
        }, "rows": [{"amount": None, "currency": None, "date": None}]}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField('asset_id', StringType()),
            StructField('status', StringType()),
            StructField('created_at', TimestampType()),
            StructField('created_by', StringType()),
            StructField('updated_at', TimestampType()),
            StructField('updated_by', StringType()),
            StructField('date', DateType()),
            StructField('currency', IntegerType()),
            StructField('amount', IntegerType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class AssetTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = ""
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset"
        self.explodables = {}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField('isin', StringType()),
            StructField('name', StringType()),
            StructField('description', StringType()),
            StructField('currency_code', IntegerType()),
            StructField('benchmark_isin', StringType()),
            StructField('is_currency_hedged', BooleanType()),
            StructField('billing_ratio', DoubleType()),
            StructField('domicile', StringType()),
            StructField('holding_type', IntegerType()),
            StructField('asset_legal_structure', IntegerType()),
            StructField('liquidity', IntegerType()),
            StructField('nav', DoubleType()),
            StructField('source', StringType()),
            StructField('status', StringType()),
            StructField('proxy_isin', StringType()),
            StructField('is_fund', BooleanType()),
            StructField('fund_type', StringType()),
            StructField('uk_reporting_status', BooleanType()),
            StructField('has_actual_price', BooleanType()),
            StructField('is_currency_override', BooleanType()),
            StructField("is_name_changed", StringType()),
            StructField("is_domicile_changed", StringType()),
            StructField("is_source_changed", StringType()),
            StructField("is_description_changed", StringType()),
            StructField("is_benchmark_isin_changed", StringType()),
            StructField("is_asset_legal_structure_changed", StringType()),
            StructField("is_fund_type_changed", StringType()),
            StructField("is_currency_code_changed", StringType()),
            StructField("is_proxy_isin_changed", StringType()),
            StructField("is_is_currency_override_changed", StringType()),
            StructField("is_nav_changed", StringType()),
            StructField("is_status_changed", StringType()),
            StructField("is_uk_reporting_status_changed", StringType()),
            StructField("is_holding_type_changed", StringType()),
            StructField("is_is_currency_hedged_changed", StringType()),
            StructField("is_liquidity_changed", StringType()),
            StructField("is_is_fund_changed", StringType()),
            StructField("is_billing_ratio_changed", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class DailyValuesTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "daily_values"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {"values": [{"date": None, "marketPrice": None, "performance": None}]}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField('isin', StringType()),
            # StructField('values', StringType()),
            StructField('date', DateType()),
            StructField('performance', DoubleType()),
            StructField('market_price', DoubleType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class PrivateCompanyInvestmentTable(TablesDynamic):

    def __init__(self, prefix):
        self.prefix = prefix
        self.file_tag = "private_company_investment"
        self.table_name = f"{db_name}.ms_asset_{prefix}_asset_{self.file_tag}"
        self.explodables = {}
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("asset_id", StringType()),
            StructField("geography_id", LongType()),
            StructField("sector_id", LongType()),
            StructField("size_id", LongType()),
            StructField("created_at", TimestampType()),
            StructField("created_by", StringType()),
            StructField("updated_at", TimestampType()),
            StructField("updated_by", StringType()),
            StructField("deleted_at", TimestampType()),
            StructField("deleted_by", StringType()),
            StructField("changes_source", StringType()),
            StructField("status", StringType()),
            StructField("file_arrival_date", DateType()),
            StructField("file_path", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    @staticmethod
    def notes():
        return """"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
