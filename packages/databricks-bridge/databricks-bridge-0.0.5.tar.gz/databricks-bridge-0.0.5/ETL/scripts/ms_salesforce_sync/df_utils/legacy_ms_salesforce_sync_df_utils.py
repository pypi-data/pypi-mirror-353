from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns

db_name = "salesforce"


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


class AccountTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "account"
        self.table_name = f"{db_name}.{self.file_tag}"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("currency", StringType()),
            StructField("account_source", StringType()),
            StructField("tier", StringType()),
            StructField("primary_employer", StringType()),
            StructField("activation_date", DateType()),
            StructField("is_internal", BooleanType()),
            StructField("family", BooleanType()),
            StructField("occupation", StringType()),
            StructField("estimated_billable_assets", DecimalType(15, 10)),
            StructField("account_record_type", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class EventsTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "events"
        self.table_name = f"{db_name}.{self.file_tag}"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("sf_id", StringType()),
            StructField("type", StringType()),
            StructField("owner_id", StringType()),
            StructField("meeting_status", StringType()),
            StructField("activity_date", DateType()),
            StructField("duration_in_minutes", IntegerType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class InvoiceTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "invoice"
        self.table_name = f"{db_name}.{self.file_tag}"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("account_id", StringType()),
            StructField("invoice_ref", StringType()),
            StructField("currency", StringType()),
            StructField("total_fee_due", DecimalType(15, 10)),
            StructField("invoice_date", DateType()),
            StructField("due_date", DateType()),
            StructField("period_from", DateType()),
            StructField("period_to", DateType()),
            StructField("status", StringType()),
            StructField("billing_rate", DecimalType(15, 10)),
            StructField("collected_from_ytree_fund", DecimalType(15, 10)),
            StructField("amount_payable", DecimalType(15, 10))
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class LeadTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "lead"
        self.table_name = f"{db_name}.{self.file_tag}"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("is_converted", DecimalType(15, 10)),
            StructField("converted_account_id", StringType()),
            StructField("converted_contact_id", StringType()),
            StructField("lead_source", StringType()),
            StructField("occupation", StringType()),
            StructField("primary_employer", StringType()),
            StructField("current_stage", StringType()),
            StructField("current_stage_date", DateType()),
            StructField("days_in_stage", DecimalType(15, 10)),
            StructField("stage_unqualified_date", DateType()),
            StructField("stage_target_date", DateType()),
            StructField("stage_contacted_date", DateType()),
            StructField("stage_pitch_meeting_set_date", DateType()),
            StructField("converted_date", DateType()),
            StructField("stage_cold_date", DateType()),
            StructField("stage_on_hold_date", DateType()),
            StructField("stage_pending_introduction_date", DateType()),
            StructField("stage_qualified_date", DateType()),
            StructField("date_unqualified_has_value", BooleanType()),
            StructField("date_target_has_value", DecimalType(15, 10)),
            StructField("date_contacted_has_value", BooleanType()),
            StructField("date_pitch_meeting_set_has_value", BooleanType()),
            StructField("date_converted_has_value", BooleanType()),
            StructField("date_cold_has_value", BooleanType()),
            StructField("date_on_hold_has_value", DecimalType(15, 10)),
            StructField("date_pending_introduction_has_value", DecimalType(15, 10)),
            StructField("date_qualified_has_value", DecimalType(15, 10))
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class OpportunityTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "opportunity"
        self.table_name = f"{db_name}.{self.file_tag}"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("account_id", StringType()),
            StructField("current_stage", StringType()),
            StructField("current_stage_date", DateType()),
            StructField("stage_initial_interaction_date", DateType()),
            StructField("stage_initial_analysis_date", DateType()),
            StructField("stage_closing_date", DateType()),
            StructField("stage_on_boarding_date", DateType()),
            StructField("stage_complete_date", DateType()),
            StructField("stage_cold_date", DateType()),
            StructField("stage_on_hold_date", DateType()),
            StructField("date_analysis_has_value", BooleanType()),
            StructField("date_closing_has_value", BooleanType()),
            StructField("date_cold_has_value", BooleanType()),
            StructField("date_complete_has_value", BooleanType()),
            StructField("date_on_boarding_has_value", BooleanType()),
            StructField("date_on_hold_has_value", BooleanType()),
            StructField("stage_qa_meeting_date", DateType()),
            StructField("stage_statement_gathering_date", DateType()),
            StructField("stage_hcls_prep_date", DateType()),
            StructField("stage_health_check_meeting_date", DateType()),
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class ProviderRelationshipTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "provider_relationship"
        self.table_name = f"{db_name}.{self.file_tag}"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("provider", StringType()),
            StructField("currency", StringType()),
            StructField("client_id", StringType()),
            StructField("relationship_number", StringType()),
            StructField("relationship_balance", DecimalType(15, 10)),
            StructField("update_frequency", DecimalType(15, 10)),
            StructField("minutes_to_update", DecimalType(15, 10)),
            StructField("data_source", StringType()),
            StructField("targeted_data_pipe", StringType()),
            StructField("data_pipe_setup_stage", StringType()),
            StructField("relationship_notes", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class ReferralsTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "referrals"
        self.table_name = f"{db_name}.{self.file_tag}"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("owner_id", StringType()),
            StructField("name", StringType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()),
            StructField("active_account_from_lead_referral", BooleanType()),
            StructField("in_progress_account_from_lead_referral", BooleanType()),
            StructField("account_referred_by", StringType()),
            StructField("lead_referred_by", StringType()),
            StructField("referred_account", StringType()),
            StructField("referred_lead", StringType()),
            StructField("stage", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class TemplateTable(TablesDynamic):

    def __init__(self):
        self.file_tag = ""
        self.table_name = f"{db_name}.{self.file_tag}"

    def create_table(self):
        return f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (

        )
        USING org.apache.spark.sql.parquet;
        """

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("", StringType()),
            StructField("", StringType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
