from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns
from ETL.commons.sql_functions import mask_pii_func
from ETL.commons.ease_of_use_fcns import get_env_catalog_name

db_name = "salesforce"
permitted_groups = ["analysts"]
catalog_name = get_env_catalog_name(catalog_name="data_warehouse")
mask_fcn_name, mask_fcn_sql = mask_pii_func(allowed_group="pii_users")
masked_column_metadata = {"mask": True, "mask_fcn": mask_fcn_name}
prerequisite_queries = [mask_fcn_sql]


def get_data_lineage(table_name):
    return {
        'target_type': "lakehouse",
        'target_endpoint': table_name,
        'src0_type': "s3",
        'src0_endpoint': "landing/salesforce/ms-salesforce-sync",
        'etl_script_path': "ETL/scripts/ms_salesforce_sync/all_ms_salesforce_sync.py",
        'src1_type': "service",
        'src1_endpoint': "ms-salesforce-sync",
        'src1_script_path': "project/api/models/"
    }


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
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("is_deleted", StringType()),
            StructField("master_record_id", StringType()),
            StructField("name", StringType(), metadata=masked_column_metadata),
            StructField("last_name", StringType(), metadata=masked_column_metadata),
            StructField("first_name", StringType(), metadata=masked_column_metadata),
            StructField("salutation", StringType()),
            StructField("middle_name", StringType(), metadata=masked_column_metadata),
            StructField("type", StringType()),
            StructField("record_type_id", StringType()),
            StructField("billing_street", StringType(), metadata=masked_column_metadata),
            StructField("billing_city", StringType(), metadata=masked_column_metadata),
            StructField("billing_state", StringType(), metadata=masked_column_metadata),
            StructField("billing_postal_code", StringType(), metadata=masked_column_metadata),
            StructField("billing_country", StringType()),
            StructField("billing_latitude", StringType(), metadata=masked_column_metadata),
            StructField("billing_longitude", StringType(), metadata=masked_column_metadata),
            StructField("billing_geocode_accuracy", StringType(), metadata=masked_column_metadata),
            StructField("billing_address", StringType(), metadata=masked_column_metadata),
            StructField("shipping_street", StringType(), metadata=masked_column_metadata),
            StructField("shipping_city", StringType(), metadata=masked_column_metadata),
            StructField("shipping_state", StringType(), metadata=masked_column_metadata),
            StructField("shipping_postal_code", StringType(), metadata=masked_column_metadata),
            StructField("shipping_country", StringType(), metadata=masked_column_metadata),
            StructField("shipping_latitude", StringType(), metadata=masked_column_metadata),
            StructField("shipping_longitude", StringType(), metadata=masked_column_metadata),
            StructField("shipping_geocode_accuracy", StringType(), metadata=masked_column_metadata),
            StructField("shipping_address", StringType(), metadata=masked_column_metadata),
            StructField("phone", StringType(), metadata=masked_column_metadata),
            StructField("website", StringType(), metadata=masked_column_metadata),
            StructField("photo_url", StringType(), metadata=masked_column_metadata),
            StructField("industry", StringType()),
            StructField("number_of_employees", StringType()),
            StructField("description", StringType(), metadata=masked_column_metadata),
            StructField("currency", StringType()),
            StructField("owner_id", StringType()),
            StructField("created_date", StringType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", StringType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", StringType()),
            StructField("last_activity_date", StringType()),
            StructField("last_viewed_date", StringType()),
            StructField("last_referenced_date", StringType()),
            StructField("person_contact_id", StringType()),
            StructField("is_person_account", BooleanType()),
            StructField("person_mailing_street", StringType(), metadata=masked_column_metadata),
            StructField("person_mailing_city", StringType(), metadata=masked_column_metadata),
            StructField("person_mailing_state", StringType(), metadata=masked_column_metadata),
            StructField("person_mailing_postal_code", StringType(), metadata=masked_column_metadata),
            StructField("person_mailing_country", StringType(), metadata=masked_column_metadata),
            StructField("person_mailing_latitude", StringType(), metadata=masked_column_metadata),
            StructField("person_mailing_longitude", StringType(), metadata=masked_column_metadata),
            StructField("person_mailing_geocode_accuracy", StringType(), metadata=masked_column_metadata),
            StructField("person_mailing_address", StringType(), metadata=masked_column_metadata),
            StructField("person_other_street", StringType(), metadata=masked_column_metadata),
            StructField("person_other_city", StringType(), metadata=masked_column_metadata),
            StructField("person_other_state", StringType(), metadata=masked_column_metadata),
            StructField("person_other_postal_code", StringType(), metadata=masked_column_metadata),
            StructField("person_other_country", StringType(), metadata=masked_column_metadata),
            StructField("person_other_latitude", StringType(), metadata=masked_column_metadata),
            StructField("person_other_longitude", StringType(), metadata=masked_column_metadata),
            StructField("person_other_geocode_accuracy", StringType(), metadata=masked_column_metadata),
            StructField("person_other_address", StringType(), metadata=masked_column_metadata),
            StructField("person_mobile_phone", StringType(), metadata=masked_column_metadata),
            StructField("person_home_phone", StringType(), metadata=masked_column_metadata),
            StructField("person_email", StringType(), metadata=masked_column_metadata),
            StructField("person_title", StringType(), metadata=masked_column_metadata),
            StructField("person_department", StringType(), metadata=masked_column_metadata),
            StructField("person_birthdate", StringType(), metadata=masked_column_metadata),
            StructField("person_last_cu_request_date", StringType()),
            StructField("person_last_cu_update_date", StringType()),
            StructField("person_email_bounced_reason", StringType()),
            StructField("person_email_bounced_date", StringType()),
            StructField("person_individual_id", StringType()),
            StructField("jigsaw", StringType()),
            StructField("jigsaw_company_id", StringType()),
            StructField("account_source", StringType()),
            StructField("sic_desc", StringType()),
            StructField("estimated_total_assets", StringType()),
            StructField("estimated_billable_assets", StringType()),
            StructField("client_classification", StringType()),
            StructField("stage", StringType()),
            StructField("referrer_full_name", StringType(), metadata=masked_column_metadata),
            StructField("y_tree_bo_id", StringType()),
            StructField("overview", StringType()),
            StructField("disclaimer_version", StringType()),
            StructField("confidentiality_promise_version", StringType()),
            StructField("disclaimer_confirmation_date", StringType()),
            StructField("confidentiality_promise_confirmation_date", StringType()),
            StructField("privacy_policy_version", StringType()),
            StructField("kyc_status__c", StringType()),
            StructField("terms_and_conditions_version", StringType()),
            StructField("terms_and_conditions_signed_date", StringType()),
            StructField("fees_version", StringType()),
            StructField("fees_confirmation_date", StringType()),
            StructField("activation_date", StringType()),
            StructField("billing_name", StringType(), metadata=masked_column_metadata),
            StructField("referral_id", StringType()),
            StructField("y_tree_back_office_link", StringType()),
            StructField("domicile", StringType()),
            StructField("tax_residency", StringType()),
            StructField("current_annual_income", StringType()),
            StructField("kyc_approved_count", StringType()),
            StructField("internal_user_profile", StringType()),
            StructField("kyc_rejected_count", StringType()),
            StructField("y_tree_champion", StringType()),
            StructField("contact_number", StringType(), metadata=masked_column_metadata),
            StructField("y_tree_bo_link", StringType()),
            StructField("y_tree_bo_error_detail", BooleanType()),
            StructField("y_tree_bo_error", StringType()),
            StructField("second_email__c", StringType(), metadata=masked_column_metadata),
            StructField("verified", StringType()),
            StructField("person_email__c", StringType(), metadata=masked_column_metadata),
            StructField("account_count", StringType()),
            StructField("g_drive_folder_id", StringType()),
            StructField("elective_professional_rejection_date", StringType()),
            StructField("total_billable_assets", FloatType()),
            StructField("terms_and_conditions_requested_date", StringType()),
            StructField("testing", StringType()),
            StructField("invoicing_period", StringType()),
            StructField("display_name", StringType(), metadata=masked_column_metadata),
            StructField("next_invoicing_start_date", StringType()),
            StructField("billing_start_date", StringType()),
            StructField("fps_expiry_date", StringType()),
            StructField("full_name", StringType(), metadata=masked_column_metadata),
            StructField("g_drive_link", StringType()),
            StructField("y_tree_risk", StringType()),
            StructField("agreed_risk_factor", StringType()),
            StructField("y_tree_bo_status", StringType()),
            StructField("primary_residency", StringType()),
            StructField("country_of_nationality", StringType()),
            StructField("primary_fee_paying_account", StringType()),
            StructField("company_type", StringType()),
            StructField("legal_structure", StringType()),
            StructField("incorporation_date", StringType()),
            StructField("incorporation_country", StringType()),
            StructField("registration_number", StringType()),
            StructField("registered_company_name", StringType()),
            StructField("web_referral_visits", StringType()),
            StructField("secondary_residency", StringType()),
            StructField("us_taxpayer", StringType()),
            StructField("stage_in_progress_date", StringType()),
            StructField("initial_opportunity", StringType()),
            StructField("minimum_fee_waived", StringType()),
            StructField("other_billing_exceptions", StringType()),
            StructField("notes_on_billing", StringType()),
            StructField("initial_pending_date", StringType()),
            StructField("initial_interaction_date", StringType()),
            StructField("initial_analysis_date", StringType()),
            StructField("initial_closing_date", StringType()),
            StructField("initial_on_boarding_date", StringType()),
            StructField("initial_complete_date", StringType()),
            StructField("initial_cold_date", StringType()),
            StructField("initial_on_hold_date", StringType()),
            StructField("lead_stage_unqualified_date", StringType()),
            StructField("lead_stage_contacted_date", StringType()),
            StructField("lead_stage_intro_meeting_set_date", StringType()),
            StructField("lead_stage_lukewarm_date", StringType()),
            StructField("lead_stage_cold_date", StringType()),
            StructField("stage_client_date", StringType()),
            StructField("stage_inactive_date", StringType()),
            StructField("stage_group_client_date", StringType()),
            StructField("onboarding", StringType()),
            StructField("last_contact", StringType()),
            StructField("y_tree_bo_link_creation_date", StringType()),
            StructField("client_classification_set_date", StringType()),
            StructField("ni_utr_set", StringType()),
            StructField("privacy_policy_confirmation_date", StringType()),
            StructField("kyc_record_count", StringType()),
            StructField("active_kyc", StringType()),
            StructField("mobile_display_name", StringType(), metadata=masked_column_metadata),
            StructField("initial_opp_estimated_billable_assets", StringType()),
            StructField("referral_url", StringType()),
            StructField("data_ramp_up_stage", StringType()),
            StructField("opportunity_ramp_up_stage", StringType()),
            StructField("multrees_payment_account_number", StringType()),
            StructField("multrees_payment_account_domicile", StringType()),
            StructField("total_billable_assets_daily_change", StringType()),
            StructField("minimum_billable_assets", StringType()),
            StructField("maximum_billable_assets", StringType()),
            StructField("last_annual_review", StringType()),
            StructField("fee", StringType()),
            StructField("is_vulnerable", BooleanType()),
            StructField("assets_under_management", FloatType()),
            StructField("marked_for_client_portal_email", StringType()),
            StructField("acquisition_email_sent_date", StringType()),
            StructField("y_tree_bo_error_retry_count", StringType()),
            StructField("tier", StringType()),
            StructField("is_child", StringType()),
            StructField("dual_nationality", StringType()),
            StructField("family", BooleanType()),
            StructField("trust_type", StringType()),
            StructField("trustees", StringType()),
            StructField("giin", StringType()),
            StructField("cash_available_in_multrees_gia", FloatType()),
            StructField("last_invoiced_amount", FloatType()),
            StructField("assets_available_in_multrees_gia", FloatType()),
            StructField("account_to_invoice", StringType()),
            StructField("initial_oppty_count", StringType()),
            StructField("job_title", StringType()),
            StructField("is_converted_from_lead__c", StringType()),
            StructField("occupation", StringType()),
            StructField("is_shareholder", BooleanType()),
            StructField("account_record_type", StringType()),
            StructField("notes", StringType()),
            StructField("subject_to_vat2", BooleanType()),
            StructField("reason_for_leaving", StringType()),
            StructField("subject_to_vat", BooleanType()),
            StructField("transactions", StringType()),
            StructField("x1_year_experience", StringType()),
            StructField("experience_details", StringType()),
            StructField("fca_registration", StringType()),
            StructField("qualitative_assessment", StringType()),
            StructField("y_tree_reviewer", StringType()),
            StructField("privacy_policy_confirmation_date2", StringType()),
            StructField("proxy_email", StringType(), metadata=masked_column_metadata),
            StructField("billable_assets", StringType()),
            StructField("account_for_invoicing", StringType()),
            StructField("account_for_blended_fee", StringType()),
            StructField("g10_reviewer", StringType()),
            StructField("y_tree_signed_off_date", StringType()),
            StructField("g10_review_date", StringType()),
            StructField("collective_investments", StringType()),
            StructField("link_to_fca_profile", StringType()),
            StructField("assessed_by", StringType()),
            StructField("tba_in_gbp", StringType()),
            StructField("personal_assistant", StringType(), metadata=masked_column_metadata),
            StructField("ni_or_utr", StringType()),
            StructField("primary_employer", StringType()),
            StructField("twilio", StringType()),
            StructField("gender", StringType()),
            StructField("twilio_provision_error", StringType()),
            StructField("twilio_provision_error_message", StringType(), metadata=masked_column_metadata),
            StructField("twilio_provision_error_detail", StringType()),
            StructField("event_account", StringType()),
            StructField("primary_contact", StringType()),
            StructField("provider", StringType()),
            StructField("link_events_to_account", StringType()),
            StructField("sub_type", StringType()),
            StructField("is_converted_from_lead__pc", StringType()),
            StructField("risk_level", StringType()),
            StructField("second_email__pc", StringType()),
            StructField("primary_employer2", StringType()),
            StructField("primary_employer3", StringType()),
            StructField("unsubscribe_product_and_service", BooleanType()),
            StructField("unsubscribe_events_and_content", BooleanType()),
            StructField("person_has_opted_out_of_email", BooleanType()),
            StructField("google_drive_link", StringType()),
            StructField("lei", StringType()),
            StructField("referred_by", StringType()),
            StructField("account_po1", StringType()),
            StructField("pod", StringType()),
            StructField("deemed_domicile", StringType()),
            StructField("sum_of_main_accounts", StringType()),
            StructField("director_s", StringType()),
            StructField("ssn_tin", StringType()),
            StructField("us_connected_person", StringType()),
            StructField("us_connected_person_notes", StringType()),
            StructField("inactive_days_count", StringType()),
            StructField("display_name__pc", StringType(), metadata=masked_column_metadata),
            StructField("twilio_re_trigger", StringType()),
            StructField("fax", StringType()),
            StructField("account_number", StringType()),
            StructField("annual_revenue", StringType()),
            StructField("site", StringType()),
            StructField("account_source_drill_down_1", StringType()),
            StructField("account_source_drill_down_2", StringType()),
            StructField("detail", StringType()),
            StructField("do_you_currently_work", StringType()),
            StructField("i_don_t_know_when_i_can_retire", BooleanType()),
            StructField("i_m_not_getting_the_best_advice", BooleanType()),
            StructField("i_m_not_sure_how_much_cash_to_hold", BooleanType()),
            StructField("i_m_not_sure_of_all_the_fees_i_pay", BooleanType()),
            StructField("industry__c", StringType()),
            StructField("my_financial_affairs_are_disorganised", BooleanType()),
            StructField("none_of_these_relate_to_me", BooleanType()),
            StructField("unaware_if_investments_are_performing", BooleanType()),
            StructField("unsure_if_i_can_sustain_my_lifestyle", BooleanType()),
            StructField("introduced_by_account", StringType()),
            StructField("introduced_by_lead", StringType()),
            StructField("client_notice_date", StringType()),
            StructField("last_billing_date", StringType()),
            StructField("termination_notice_via", StringType()),
            StructField("end_of_notice_period_date", StringType()),
            StructField("corporate_agreement", StringType()),
            StructField("trading_restrictions", StringType()),
            StructField("how_did_you_hear_about_us", StringType()),
            StructField("other_details_how_did_you_hear", StringType()),
            StructField("has_invoicing_contact", BooleanType()),
            StructField("invoicing_contact_count", DoubleType()),
            StructField("call_type", StringType()),
            StructField("referee", StringType()),
            StructField("date_client_became_vulnerable", DateType()),
            StructField("person_age", DoubleType()),
            StructField("bo_update_flag", BooleanType()),
            StructField("role_tenure", StringType()),
            StructField("tax_residency__c", StringType()),
            StructField("bo_update_date", TimestampType()),
            StructField("family_type", StringType()),
            StructField("create_group_account", BooleanType()),
            StructField("risk_score", DoubleType()),
            StructField("acquisition_channel", StringType()),
            StructField("date_onboarding_email_sent", DateType()),
            StructField("onboarding_email_sent", BooleanType()),
            StructField("send_onboarding_email", BooleanType()),
            StructField("utr_number", StringType()),
            StructField("is_force_kyc_refresh", DateType()),
            StructField("is_kyc_automated_expiry_email_sent", BooleanType()),
            StructField("utm_campaign_id", StringType()),
            StructField("utm_channel_id", StringType()),
            StructField("utm_medium_id", StringType()),
            StructField("utm_source_id", StringType()),
            StructField("questionnaire_completion_date", DateType()),
            StructField("client_portal_registration_date", DateType()),
            StructField("rebalanced_portfolio_service", StringType()),
            StructField("maiden_name", StringType(), metadata=masked_column_metadata),
            StructField("professional_full_name", StringType(), metadata=masked_column_metadata),
            StructField("rps_effective_date", DateType()),
            StructField("total_billable_assets_daily_change_old", DoubleType()),
            StructField("country_of_birth", StringType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class AssociationTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "association"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("owner_id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("name", StringType()),
            StructField("currency", StringType()),
            StructField("record_type_id", StringType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("left_account", StringType()),
            StructField("right_account", StringType()),
            StructField("relationship", StringType()),
            StructField("display_activity", BooleanType()),
            StructField("uid", StringType()),
            StructField("primary", StringType()),
            StructField("is_left_account_on_back_office", StringType()),
            StructField("is_right_account_on_back_office", StringType()),
            StructField("provider", StringType()),
            StructField("left_account_record_type_id", StringType()),
            StructField("right_account_record_type_id", StringType()),
            StructField("invoicing_contact", BooleanType()),
            StructField("is_person_account", BooleanType()),
            StructField("is_internal_profile", BooleanType()),
            StructField("app_access", StringType()),
            StructField("client_portal_access", StringType()),
            StructField("corporate_relationship", StringType()),
            StructField("family_relation", BooleanType()),
            StructField("left_account_stage", StringType()),
            StructField("profile_owner", BooleanType()),
            StructField("relation_to_right_account", StringType()),
            StructField("right_account_stage", StringType()),
            StructField("relation_to_left_account", StringType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class CaseTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "case"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("is_deleted",  BooleanType()), 
            StructField("master_record_id",  StringType()), 
            StructField("case_number",  StringType()), 
            StructField("contact_id",  StringType()), 
            StructField("account_id",  StringType()), 
            StructField("asset_id",  StringType()), 
            StructField("source_id",  StringType()), 
            StructField("business_hours_id",  StringType()), 
            StructField("parent_id",  StringType()), 
            StructField("supplied_name",  StringType(), metadata=masked_column_metadata),
            StructField("supplied_email",  StringType(), metadata=masked_column_metadata),
            StructField("supplied_phone",  StringType(), metadata=masked_column_metadata),
            StructField("supplied_company",  StringType(), metadata=masked_column_metadata),
            StructField("type",  StringType()), 
            StructField("record_type_id",  StringType()), 
            StructField("status",  StringType()), 
            StructField("reason",  StringType()), 
            StructField("origin",  StringType()), 
            StructField("subject",  StringType()), 
            StructField("priority",  StringType()), 
            StructField("description",  StringType()), 
            StructField("is_closed",  BooleanType()), 
            StructField("closed_date",  StringType()), 
            StructField("is_escalated",  BooleanType()), 
            StructField("currency_iso_code",  StringType()), 
            StructField("owner_id",  StringType()), 
            StructField("is_closed_on_create",  StringType()), 
            StructField("created_date",  StringType()), 
            StructField("created_by_id",  StringType()), 
            StructField("last_modified_date",  StringType()), 
            StructField("last_modified_by_id",  StringType()), 
            StructField("system_modstamp",  StringType()), 
            StructField("contact_phone",  StringType(), metadata=masked_column_metadata),
            StructField("contact_mobile",  StringType(), metadata=masked_column_metadata),
            StructField("contact_email",  StringType(), metadata=masked_column_metadata),
            StructField("contact_fax",  StringType(), metadata=masked_column_metadata),
            StructField("comments",  StringType()), 
            StructField("last_viewed_date",  StringType()), 
            StructField("last_referenced_date",  StringType()), 
            StructField("compensation_paid_by_y_tree",  DoubleType()), 
            StructField("complainant",  StringType(), metadata=masked_column_metadata),
            StructField("complaint_upheld_by_y_tree",  BooleanType()), 
            StructField("consumer_duty_flag",  StringType()), 
            StructField("date_complaint_received",  StringType()), 
            StructField("fos_review_outcome",  StringType()), 
            StructField("final_response_letter_sent_date",  StringType()), 
            StructField("further_information",  StringType()), 
            StructField("initial_response_letter_sent_date",  StringType()), 
            StructField("interim_letter_sent_date",  StringType()), 
            StructField("precise_details_of_complaint",  StringType()), 
            StructField("reason_for_closing",  StringType()), 
            StructField("root_cause",  StringType()), 
            StructField("submitted_by",  StringType()), 
            StructField("y_tree_review_sign_off_by",  StringType()), 
            StructField("client_classification",  StringType()), 
            StructField("deadline_for_escalating_to_fos",  StringType()), 
            StructField("final_response_letter_due_date",  StringType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
    

class CompanyTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "company"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("owner_id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("name", StringType()),
            StructField("currency", StringType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("last_activity_date", StringType()),
            StructField("last_viewed_date", StringType()),
            StructField("last_referenced_date", StringType()),
            StructField("notes", StringType()),
            StructField("industry", StringType()),
            StructField("number_of_partners", StringType()),
            StructField("average_size_of_client", StringType()),
            StructField("leads", StringType()),
            StructField("opportunities", StringType()),
            StructField("clients_opportunities", StringType()),
            StructField("average_billable_assets", DoubleType()),
            StructField("penetration_rate", DoubleType()),
            StructField("rating", StringType()),
            StructField("total_potential_billable_assets", DoubleType()),
            StructField("prospects_ba_opportunity", DoubleType()),
            StructField("prospects", DoubleType()),
            StructField("strategy", StringType()),
            StructField("strategy_more_details", StringType()),
            StructField("next_group_meeting", StringType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class ContactTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "contact"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("master_record_id", StringType()),
            StructField("account_id", StringType()),
            StructField("is_person_account", BooleanType()),
            StructField("last_name", StringType(), metadata=masked_column_metadata),
            StructField("first_name", StringType(), metadata=masked_column_metadata),
            StructField("salutation", StringType()),
            StructField("middle_name", StringType(), metadata=masked_column_metadata),
            StructField("name", StringType(), metadata=masked_column_metadata),
            StructField("mailing_street", StringType(), metadata=masked_column_metadata),
            StructField("mailing_city", StringType(), metadata=masked_column_metadata),
            StructField("mailing_state", StringType(), metadata=masked_column_metadata),
            StructField("mailing_postal_code", StringType(), metadata=masked_column_metadata),
            StructField("mailing_country", StringType(), metadata=masked_column_metadata),
            StructField("mailing_latitude", StringType(), metadata=masked_column_metadata),
            StructField("mailing_longitude", StringType(), metadata=masked_column_metadata),
            StructField("mailing_geocode_accuracy", StringType(), metadata=masked_column_metadata),
            StructField("mailing_address", StringType(), metadata=masked_column_metadata),
            StructField("phone", StringType(), metadata=masked_column_metadata),
            StructField("fax", StringType(), metadata=masked_column_metadata),
            StructField("mobile_phone", StringType(), metadata=masked_column_metadata),
            StructField("home_phone", StringType(), metadata=masked_column_metadata),
            StructField("reports_to_id", FloatType()),
            StructField("email", StringType(), metadata=masked_column_metadata),
            StructField("title", StringType()), 
            StructField("department", StringType()),
            StructField("birthdate", StringType(), metadata=masked_column_metadata),
            StructField("currency_iso_code", StringType()),
            StructField("owner_id", StringType()),
            StructField("has_opted_out_of_email", BooleanType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()), 
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("last_activity_date", StringType()),
            StructField("last_cu_request_date", StringType()),
            StructField("last_cu_update_date", StringType()), 
            StructField("last_viewed_date", StringType()),
            StructField("last_referenced_date", StringType()), 
            StructField("email_bounced_reason", StringType()),
            StructField("email_bounced_date", StringType()),
            StructField("is_email_bounced", StringType()),
            StructField("photo_url", StringType()),
            StructField("jigsaw", StringType()),
            StructField("jigsaw_contact_id", StringType(), metadata=masked_column_metadata),
            StructField("individual_id", StringType()), 
            StructField("display_name", StringType(), metadata=masked_column_metadata),
            StructField("ni_or_utr", StringType()),
            StructField("personal_assistant", StringType(), metadata=masked_column_metadata),
            StructField("primary_employer", StringType()),
            StructField("twilio_provision_error_detail", StringType()),
            StructField("twilio_provision_error", StringType()), 
            StructField("twilio_provision_error_message", StringType()),
            StructField("twilio", StringType(), metadata=masked_column_metadata),
            StructField("provider", StringType()), 
            StructField("gender", StringType()),
            StructField("event_account", StringType()),
            StructField("link_events_to_account", StringType()),
            StructField("sub_type", StringType()),
            StructField("second_email", StringType(), metadata=masked_column_metadata),
            StructField("risk_level", StringType()),
            StructField("primary_employer2", StringType()), 
            StructField("primary_employer3", StringType()),
            StructField("unsubscribe_events_and_content", BooleanType()),
            StructField("unsubscribe_product_and_service", BooleanType()),
            StructField("twilio_re_trigger", StringType()),
            StructField("create_group_account", BooleanType()),
            StructField("risk_score", DoubleType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
    

class CreditNoteTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "credit_note"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("owner_id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("name", StringType(), metadata=masked_column_metadata),
            StructField("currency_iso_code", StringType()),
            StructField("created_date", StringType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", StringType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", StringType()),
            StructField("last_activity_date", StringType()),
            StructField("last_viewed_date", StringType()),
            StructField("last_referenced_date", StringType()),
            StructField("account", StringType(), metadata=masked_column_metadata),
            StructField("credit_note_date", StringType()),
            StructField("link_to_the_request_form", StringType()),
            StructField("management_notes", StringType(), metadata=masked_column_metadata),
            StructField("pdf_generation_queued", BooleanType()),
            StructField("period_from", StringType()),
            StructField("period_to", StringType()),
            StructField("status", StringType()),
            StructField("total_to_be_credited", StringType()),
            StructField("vat_rate", DoubleType()),
            StructField("vat", DoubleType()),
            StructField("total_items_fee", DoubleType()),
            StructField("total_refund_amount", DoubleType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class EmailMessageTable(TablesDynamic):
    def __init__(self):
        self.file_tag = "email_message"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("parent_id", StringType()),
            StructField("activity_id", StringType()),
            StructField("created_by_id", StringType()),
            StructField("created_date", TimestampType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("from_name", StringType()),
            StructField("from_address", StringType()),
            StructField("validated_from_address", StringType()),
            StructField("to_address", StringType()),
            StructField("cc_address", StringType()),
            StructField("bcc_address", StringType()),
            StructField("incoming", BooleanType()),
            StructField("has_attachment", BooleanType()),
            StructField("status", LongType()),
            StructField("message_date", TimestampType()),
            StructField("is_deleted", BooleanType() ),
            StructField("reply_to_email_message_id", StringType()),
            StructField("is_externally_visible", BooleanType()),
            StructField("message_identifier", StringType()),
            StructField("thread_identifier", StringType()),
            StructField("is_client_managed", BooleanType()),
            StructField("related_to_id", StringType()),
            StructField("is_tracked", BooleanType() ),
            StructField("is_opened", BooleanType()),
            StructField("first_opened_date", StringType()),
            StructField("last_opened_date", StringType()),
            StructField("is_bounced", BooleanType()),
            StructField("email_template_id", StringType()),
            # StructField("recurrence_time_zone_sid_key", IntegerType()),
            # StructField("recurrence_type", IntegerType()),
            # StructField("recurrence_interval", IntegerType()),
            # StructField("recurrence_day_of_week_mask", IntegerType()),
            # StructField("recurrence_day_of_month", IntegerType()),
            # StructField("recurrence_instance", IntegerType()),
            # StructField("recurrence_month_of_year", IntegerType()),
            # StructField("recurrence_regenerated_type", IntegerType()),
            # StructField("task_subtype", StringType()),
            # StructField("completed_date_time", StringType()),
            # StructField("slscore_formatted_end_date_time", IntegerType()),
            # StructField("slscore_formatted_start_date_time", IntegerType()),
            # StructField("active_time_log", BooleanType()),
            # StructField("time_log_type", StringType()),
            # StructField("update_related_to", BooleanType()),
            # StructField("workflow_timer_formula", StringType())
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class EventTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "events"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{db_name}.event_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("record_type_id", StringType()),
            StructField("who_id", StringType()),
            StructField("what_id", StringType()),
            StructField("who_count", StringType()),
            StructField("what_count", StringType()),
            StructField("subject", StringType()),
            StructField("location", StringType()),
            StructField("is_all_day_event", BooleanType()),
            StructField("activity_date_time", TimestampType()),
            StructField("activity_date", DateType()),
            StructField("duration_in_minutes", StringType()),
            StructField("start_date_time", TimestampType()),
            StructField("end_date_time", TimestampType()),
            StructField("end_date", DateType()),
            StructField("description", StringType()),
            StructField("sf_id", StringType()),
            StructField("owner_id", StringType()),
            StructField("currency", StringType()),
            StructField("type", StringType()),
            StructField("is_private", BooleanType()),
            StructField("show_as", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("is_child", BooleanType()),
            StructField("is_group_event", BooleanType()),
            StructField("group_event_type", StringType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("is_archived", BooleanType()),
            StructField("recurrence_activity_id", StringType()),
            StructField("is_recurrence", BooleanType()),
            StructField("recurrence_start_date_time", StringType()),
            StructField("recurrence_end_date_only", StringType()),
            StructField("recurrence_time_zone_sid_key", StringType()),
            StructField("recurrence_type", StringType()),
            StructField("recurrence_interval", StringType()),
            StructField("recurrence_day_of_week_mask", StringType()),
            StructField("recurrence_day_of_month", StringType()),
            StructField("recurrence_instance", StringType()),
            StructField("recurrence_month_of_year", StringType()),
            StructField("reminder_date_time", TimestampType()),
            StructField("is_reminder_set", BooleanType()),
            StructField("event_subtype", StringType()),
            StructField("is_recurrence2_exclusion", BooleanType()),
            StructField("recurrence2_pattern_text", StringType()),
            StructField("recurrence2_pattern_version", StringType()),
            StructField("is_recurrence2", BooleanType()),
            StructField("is_recurrence2_exception", BooleanType()),
            StructField("recurrence2_pattern_start_date", StringType()),
            StructField("recurrence2_pattern_time_zone", StringType()),
            StructField("meeting_status", StringType()),
            StructField("recording_url", StringType()),
            StructField("recording_link", StringType()),
            StructField("twilio_error_details", StringType()),
            StructField("who_name", StringType(), metadata=masked_column_metadata),
            StructField("what_name", StringType(), metadata=masked_column_metadata),
            StructField("slscore_formatted_end_date_time", StringType()),
            StructField("slscore_formatted_start_date_time", StringType()),
            StructField("question_1", StringType()),
            StructField("question_2", StringType()),
            StructField("question_3", StringType()),
            StructField("question_4", StringType()),
            StructField("question_5", StringType()),
            StructField("active_time_log", StringType()),
            StructField("time_log_type", StringType()),
            StructField("workflow_timer_formula", TimestampType()),
            StructField("update_related_to", BooleanType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class InvoiceTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "invoice"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("owner_id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("invoice_ref", StringType()),
            StructField("currency", StringType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("last_activity_date", DateType()),
            StructField("last_viewed_date", TimestampType()),
            StructField("last_referenced_date", TimestampType()),
            StructField("account_id", StringType()),
            StructField("period_from", DateType()),
            StructField("period_to", DateType()),
            StructField("invoice_date", DateType()),
            StructField("payment_terms_days", StringType()),
            StructField("due_date", DateType()),
            StructField("avg_y_tree_assets_for_the_period", DoubleType()),
            StructField("total_fee_due", DoubleType()),
            StructField("collected_from_ytree_fund", DoubleType()),
            StructField("avg_billable_assets_for_the_period", DoubleType()),
            StructField("current_billable_assets", DoubleType()),
            StructField("multrees_payment_account_domicile", StringType()),
            StructField("current_y_tree_assets", DoubleType()),
            StructField("vat_rate", DoubleType()),
            StructField("cash_available_for_fee_collection", DoubleType()),
            StructField("multrees_payment_account_number", StringType()),
            StructField("other_assets_available_for_feecollection", DoubleType()),
            StructField("account_to_invoice", StringType()),
            StructField("billing_rate", DoubleType()),
            StructField("amount_payable_override", DoubleType()),
            StructField("management_notes", StringType()),
            StructField("date_reviewed_by_ops", DateType()),
            StructField("review", StringType()),
            StructField("date_reviewed_by_advice", DateType()),
            StructField("date_approved_by_management", DateType()),
            StructField("date_viewed_by_client", DateType()),
            StructField("pdf_generation_queued", BooleanType()),
            StructField("invoicing_contact_count", DoubleType()),
            StructField("bypass_validation", BooleanType()),
            StructField("status", StringType()),
            StructField("vat", DoubleType()),
            StructField("total_amount_payable", DoubleType()),
            StructField("amount_payable", DoubleType()),
            StructField("expected_fee_direct_from_client", DoubleType()),
            StructField("expected_fee_from_assets_available", DoubleType()),
            StructField("expected_fee_from_cash_available", DoubleType()),
            StructField("rebate_amount", DoubleType()),
            StructField("requires_manual_review", StringType()),
            StructField("tm_weighted_average_assets", DoubleType()),
            StructField("non_tm_weighted_average_assets", DoubleType()),
            StructField("tm_fee_rate", DoubleType()),
            StructField("non_tm_fee_rate", DoubleType()),
            StructField("tm_fee", DoubleType()),
            StructField("non_tm_fee", DoubleType()),
            StructField("multrees_account_funding", DoubleType()),
            StructField("prevent_popup_msg", BooleanType()),
            StructField("total_family_invoice_amount", DoubleType()),
            StructField("total_amount_payable2", DoubleType()),
            StructField("custodian_amount_to_be_calculated", BooleanType()),
            StructField("expected_family_fee_direct_from_client", DoubleType()),
            StructField("expected_fee_direct_from_client2", DoubleType()),
            StructField("is_child", BooleanType()),
            StructField("parent_account_multrees_balance", DoubleType()),
            StructField("invoice_paid_date", DateType()),
            StructField("invoice_sent_date", DateType()),
            StructField("invoice_void_date", DateType()),
            StructField("pending_advice_approval_date", DateType()),
            StructField("pending_management_date", DateType()),
            StructField("pending_ops_date", DateType()),
            StructField("push_to_next_period_date", DateType()),
            StructField("ready_to_send_date", DateType()),
            StructField("collected_custody_amount", DoubleType()),
            StructField("invoice_pdf_id", StringType()),
            StructField("primary_family_invoice", StringType()),
            StructField("account_tier", StringType()),
            StructField("account_for_invoice", StringType()),
            StructField("payment_method", StringType()),
            StructField("raised_for_collection", BooleanType()),
            StructField("account_rec_type", StringType()),
            StructField("health_check_invoice", BooleanType()),
            StructField("total_partial_payment_amount", DoubleType()),
            StructField("total_family_partial_payments", DoubleType()),
            StructField("total_family_multrees_collections", DoubleType()),
            StructField("account_stage", StringType()),
            StructField("end_of_notice_period_date", DateType()),
            StructField("invoice_id", StringType()),
            StructField("billing_calc_content_version_id", StringType()),
            StructField("payment_due", DoubleType()),
            StructField("total_family_payment_due", DoubleType()),
            StructField("total_family_redress", DoubleType()),
            StructField("total_family_sipp_collection", DoubleType()),
            StructField("sipp_collection", DoubleType()),
            StructField("total_redress", DoubleType()),
            StructField("primary_invoice_status", StringType()),
            StructField("account_internal_profile", BooleanType()),
            StructField("total_direct_payments", DoubleType()),
            StructField("direct_payments", DoubleType()),
            StructField("multri_account_total_amount", DoubleType()),
            StructField("total_family_amount_for_child", DoubleType()),
            StructField("account_family_type", StringType()),
            StructField("account_id_alt", StringType()),
            StructField("days_difference", DoubleType()),
            StructField("account_family_type1", StringType()),
            StructField("bo_status", StringType()),
            StructField("bo_failed_reason", StringType()),
            StructField("avg_billable_assets_for_the_period2", DoubleType()),
            StructField("billing_rate2", DoubleType()),
            StructField("is_old_billing", BooleanType()),
            StructField("vat2", DoubleType()),
            StructField("bespoke_family_billable_assets", DoubleType()),
            StructField("bespoke_family_fee", DoubleType()),
            StructField("bespoke_family_vat", DoubleType()),
            StructField("bespoke_fee_rate", DoubleType()),
            StructField("bespoke_services_billable_assets", DoubleType()),
            StructField("bespoke_services_fee", DoubleType()),
            StructField("bespoke_vat", DoubleType()),
            StructField("core_family_billable_assets", DoubleType()),
            StructField("core_family_fee", DoubleType()),
            StructField("core_family_vat", DoubleType()),
            StructField("core_fee_rate", DoubleType()),
            StructField("core_services_fee", DoubleType()),
            StructField("rps_billable_assets", DoubleType()),
            StructField("rps_family_billable_assets", DoubleType()),
            StructField("rps_family_fee", DoubleType()),
            StructField("rps_fee_due", DoubleType()),
            StructField("rps_fee_rate", DoubleType()),
            StructField("bespoke_family_fee_rate", DoubleType()),
            StructField("core_family_fee_rate", DoubleType()),
            StructField("family_summary_fee_rate", DoubleType()),
            StructField("rps_family_fee_rate", DoubleType()),
            StructField("payment_due_date", DateType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class LeadTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "lead"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("master_record_id", StringType()),
            StructField("last_name", StringType(), metadata=masked_column_metadata),
            StructField("first_name", StringType(), metadata=masked_column_metadata),
            StructField("salutation", StringType()),
            StructField("middle_name", StringType(), metadata=masked_column_metadata),
            StructField("name", StringType(), metadata=masked_column_metadata),
            StructField("title", StringType()),
            StructField("company", StringType()),
            StructField("street", StringType(), metadata=masked_column_metadata),
            StructField("city", StringType(), metadata=masked_column_metadata),
            StructField("state", StringType(), metadata=masked_column_metadata),
            StructField("postal_code", StringType(), metadata=masked_column_metadata),
            StructField("country", StringType()),
            StructField("latitude", StringType(), metadata=masked_column_metadata),
            StructField("longitude", StringType(), metadata=masked_column_metadata),
            StructField("geocode_accuracy", StringType(), metadata=masked_column_metadata),
            StructField("address", StringType(), metadata=masked_column_metadata),
            StructField("phone", StringType(), metadata=masked_column_metadata),
            StructField("mobile_phone", StringType(), metadata=masked_column_metadata),
            StructField("email", StringType(), metadata=masked_column_metadata),
            StructField("website", StringType(), metadata=masked_column_metadata),
            StructField("photo_url", StringType()),
            StructField("lead_source", StringType()),
            StructField("current_stage", StringType()),
            StructField("industry", StringType()),
            StructField("rating", StringType()),
            StructField("currency", StringType()),
            StructField("number_of_employees", StringType()),
            StructField("owner_id", StringType()),
            StructField("is_converted", BooleanType()),
            StructField("converted_date", StringType()),
            StructField("converted_account_id", StringType()),
            StructField("converted_contact_id", StringType()),
            StructField("converted_opportunity_id", StringType()),
            StructField("is_unread_by_owner", BooleanType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("last_activity_date", DateType()),
            StructField("last_viewed_date", StringType()),
            StructField("last_referenced_date", StringType()),
            StructField("jigsaw", StringType()),
            StructField("jigsaw_contact_id", StringType()),
            StructField("email_bounced_reason", StringType()),
            StructField("email_bounced_date", TimestampType()),
            StructField("individual_id", StringType()),
            StructField("pa_full_name", StringType(), metadata=masked_column_metadata),
            StructField("pa_telephone", StringType()),
            StructField("pa_email", StringType()),
            StructField("estimated_billable_assets", StringType()),
            StructField("estimated_total_assets", StringType()),
            StructField("referral_id", StringType()),
            StructField("stage_unqualified_date", DateType()),
            StructField("primary_employer", StringType()),
            StructField("stage_contacted_date", StringType()),
            StructField("y_tree_champion", StringType()),
            StructField("current_stage_date", DateType()),
            StructField("task_generation_review_lead_status", StringType()),
            StructField("stage_pitch_meeting_set_date", DateType()),
            StructField("stage_lukewarm_date", StringType()),
            StructField("stage_cold_date", StringType()),
            StructField("send_meeting_request_notification", BooleanType()),
            StructField("stage_on_hold_date", DateType()),
            StructField("date_cold_has_value", StringType()),
            StructField("date_contacted_has_value", StringType()),
            StructField("date_intro_meeting_set_has_value", StringType()),
            StructField("date_unqualified_has_value", StringType()),
            StructField("date_is_lead_has_value", StringType()),
            StructField("meeting_requested_date", DateType()),
            StructField("date_on_hold_has_value", StringType()),
            StructField("date_converted_Has_value74", StringType()),
            StructField("occupation", StringType()),
            StructField("is_intermediary", BooleanType()),
            StructField("intermediary", StringType()),
            StructField("days_since_creation", StringType()),
            StructField("stage_target_date", StringType()),
            StructField("stage_pending_introduction_date", StringType()),
            StructField("stage_converted_date", StringType()),
            StructField("date_target_has_value", StringType()),
            StructField("date_pending_introduction_has_value", StringType()),
            StructField("date_pitch_meet_set_has_value", StringType()),
            StructField("referrer_from_website", StringType()),
            StructField("result_of_website_referral", StringType()),
            StructField("residency", StringType()),
            StructField("reason", StringType()),
            StructField("days_in_stage", StringType()),
            StructField("job_title", StringType()),
            StructField("is_shareholder", BooleanType()),
            StructField("sub_type", StringType()),
            StructField("lead_convert_check", BooleanType()),
            StructField("primary_employer2", StringType()),
            StructField("unsubscribe_events_and_content", BooleanType()),
            StructField("unsubscribe_product_and_service", BooleanType()),
            StructField("referral_url", StringType()),
            StructField("lead_source_drill_down_1", StringType()),
            StructField("lead_source_drill_down_2", StringType()),
            StructField("referrer_full_name", StringType(), metadata=masked_column_metadata),
            StructField("referred_by", StringType()),
            StructField("lead_notes", StringType()),
            StructField("lead_priority", StringType()),
            StructField("einstein_rating", StringType()),
            StructField("lead_po_1", StringType()),
            StructField("last_touch_point_with_referrer", StringType()),
            StructField("expected_next", StringType()),
            StructField("new_funnel_lead_score", StringType()),
            StructField("stage_at_time_of_12_21_funnel_update", StringType()),
            StructField("stage_qualified_date", StringType()),
            StructField("estimated_investable_assets_from_website", StringType()),
            StructField("second_email", StringType(), metadata=masked_column_metadata),
            StructField("eo_campaigns_id", StringType()),
            StructField("date_pitch_meeting_set_has_value", StringType()),
            StructField("date_converted_has_value115", StringType()),
            StructField("date_qualified_has_value", StringType()),
            StructField("lead_score", StringType()),
            StructField("date_converted_has_value", BooleanType()),
            StructField("fax", StringType()),
            StructField("description", StringType()),
            StructField("annual_revenue", StringType()),
            StructField("has_opted_out_of_email", BooleanType()),
            StructField("do_not_call", BooleanType()),
            StructField("has_opted_out_of_fax", BooleanType()),
            StructField("last_transfer_date", DateType()),
            StructField("detail", StringType()),
            StructField("do_you_currently_work", StringType()),
            StructField("i_don_t_know_when_i_can_retire", BooleanType()),
            StructField("i_m_not_getting_the_best_advice", BooleanType()),
            StructField("i_m_not_sure_how_much_cash_to_hold", BooleanType()),
            StructField("i_m_not_sure_of_all_the_fees_i_pay", BooleanType()),
            StructField("industry__c", StringType()),
            StructField("my_financial_affairs_are_disorganised", BooleanType()),
            StructField("none_of_these_relate_to_me", BooleanType()),
            StructField("unaware_if_investments_are_performing", BooleanType()),
            StructField("unsure_if_i_can_sustain_my_lifestyle", BooleanType()),
            StructField("introduced_by_account", StringType()),
            StructField("introduced_by_lead", StringType()),
            StructField("internal_user_profile", BooleanType()),
            StructField("stage_new_date", DateType()),
            StructField("date_new_has_value", DoubleType()),
            StructField("pa_first_name", StringType()),
            StructField("pa_last_name", StringType()),
            StructField("how_did_you_hear_about_us", StringType()),
            StructField("other_details_how_did_you_hear", StringType()),
            StructField("lead_not_contacted", BooleanType()),
            StructField("facebook_click_id", StringType()),
            StructField("google_ad_click_id", StringType()),
            StructField("first_touch_converting_campaign_hs", StringType()),
            StructField("last_touch_converting_campaign_hs", StringType()),
            StructField("job_title_website", StringType()),
            StructField("estimated_investable_assets_from_social", StringType()),
            StructField("create_group_account", BooleanType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class OpportunityTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "opportunity"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("account_id", StringType()),
            StructField("record_type_id", StringType()),
            StructField("name", StringType(), metadata=masked_column_metadata),
            StructField("description", StringType()),
            StructField("current_stage", StringType()),
            StructField("amount", StringType()),
            StructField("probability", StringType()),
            StructField("close_date", DateType()),
            StructField("type", StringType()),
            StructField("next_step", StringType()),
            StructField("lead_source", StringType()),
            StructField("is_closed", BooleanType()),
            StructField("is_won", BooleanType()),
            StructField("forecast_category", StringType()),
            StructField("forecast_category_name", StringType()),
            StructField("currency", StringType()),
            StructField("campaign_id", StringType()),
            StructField("has_opportunity_line_item", BooleanType()),
            StructField("pricebook2_id", StringType()),
            StructField("owner_id", StringType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("last_activity_date", StringType()),
            StructField("fiscal_quarter", StringType()),
            StructField("fiscal_year", StringType()),
            StructField("fiscal", StringType()),
            StructField("contact_id", StringType()),
            StructField("last_viewed_date", StringType()),
            StructField("last_referenced_date", StringType()),
            StructField("synced_quote_id", StringType()),
            StructField("contract_id", StringType()),
            StructField("has_open_activity", BooleanType()),
            StructField("has_overdue_task", BooleanType()),
            StructField("last_amount_changed_history_id", StringType()),
            StructField("last_close_date_changed_history_id", StringType()),
            StructField("budget_confirmed", BooleanType()),
            StructField("discovery_completed", BooleanType()),
            StructField("roi_analysis_completed", BooleanType()),
            StructField("loss_reason", StringType()),
            StructField("trigger_date", StringType()),
            StructField("expected_fee_rate", StringType()),
            StructField("expected_fee", StringType()),
            StructField("weighted_expected_fee", StringType()),
            StructField("current_stage_date", DateType()),
            StructField("onboard_notification_due", BooleanType()),
            StructField("act_billable_assets", StringType()),
            StructField("act_complete_date", StringType()),
            StructField("est_act_aua_date", StringType()),
            StructField("est_act_aua_billable", StringType()),
            StructField("is_account_on_back_office", BooleanType()),
            StructField("total_days_in_pending", StringType()),
            StructField("send_acquisition_emails", BooleanType()),
            StructField("ready_to_send_acquisition_emails", BooleanType()),
            StructField("account_email", StringType(), metadata=masked_column_metadata),
            StructField("primary_contact", StringType()),
            StructField("acquisition_email_status", StringType()),
            StructField("days_in_current_stage", StringType()),
            StructField("reason", StringType()),
            StructField("owner_mobile_phone", StringType(), metadata=masked_column_metadata),
            StructField("is_converted_from_lead", BooleanType()),
            StructField("bypass_validation", BooleanType()),
            StructField("last_stage_info_refresh_date", DateType()),
            StructField("est_billable_assets_from_lead_conversion", StringType()),
            StructField("stage_pending_date", StringType()),
            StructField("stage_initial_interaction_date", DateType()),
            StructField("stage_initial_analysis_date", DateType()),
            StructField("stage_closing_date", DateType()),
            StructField("stage_on_boarding_date", DateType()),
            StructField("stage_complete_date", DateType()),
            StructField("stage_cold_date", DateType()),
            StructField("stage_on_hold_date", DateType()),
            StructField("primary_contact_first_name", StringType(), metadata=masked_column_metadata),
            StructField("increase_type", StringType()),
            StructField("est_billable_copy", StringType()),
            StructField("days_between_pending_complete", StringType()),
            StructField("days_between_interaction_complete", StringType()),
            StructField("days_between_analysis_complete", StringType()),
            StructField("days_between_closing_complete", StringType()),
            StructField("days_between_onboarding_complete", StringType()),
            StructField("days_between_cold_completed", StringType()),
            StructField("days_between_on_hold_completed", StringType()),
            StructField("days_pending_complete_has_value", StringType()),
            StructField("days_interaction_complete_has_value", StringType()),
            StructField("days_analysis_complete_has_value", StringType()),
            StructField("days_closing_complete_has_value", StringType()),
            StructField("days_onboarding_complete_has_value", StringType()),
            StructField("days_cold_complete_has_value", StringType()),
            StructField("days_on_hold_complete_has_value", StringType()),
            StructField("days_in_completed_has_value", StringType()),
            StructField("date_analysis_has_value", StringType()),
            StructField("date_closing_has_value", StringType()),
            StructField("date_interaction_has_value", StringType()),
            StructField("date_on_boarding_has_value", StringType()),
            StructField("date_on_hold_has_value", StringType()),
            StructField("date_cold_has_value", StringType()),
            StructField("date_complete_has_value", StringType()),
            StructField("total_days_in_initial_interaction", StringType()),
            StructField("total_days_in_initial_analysis", StringType()),
            StructField("total_days_in_closing", StringType()),
            StructField("total_days_in_on_boarding", StringType()),
            StructField("total_days_in_on_hold", StringType()),
            StructField("total_days_in_cold", StringType()),
            StructField("total_days_in_complete", StringType()),
            StructField("stage_qa_meeting_date", DateType()),
            StructField("stage_statement_gathering_date", DateType()),
            StructField("stage_hcls_prep_date", DateType()),
            StructField("stage_health_check_meeting_date", DateType()),
            StructField("total_days_in_q_a_meeting", StringType()),
            StructField("total_days_in_statement_gathering", StringType()),
            StructField("total_days_in_hc_ls_prep", StringType()),
            StructField("total_days_in_hc_meeting", StringType()),
            StructField("days_between_qa_meeting_complete", StringType()),
            StructField("days_between_sgathering_complete", StringType()),
            StructField("days_between_hc_prep_complete", StringType()),
            StructField("days_between_hc_meeting_complete", StringType()),
            StructField("opp_po1", StringType()),
            StructField("formatted_est_billable_assets", StringType()),
            StructField("date_interaction_has_value_250619", StringType()),
            StructField("send_q_a_prep_email_date", StringType()),
            StructField("send_q_a_prep_email_flag", BooleanType()),
            StructField("q_a_meeting_status", StringType()),
            StructField("account_fee_schedule", StringType()),
            StructField("health_check_invoice", BooleanType()),
            StructField("other_details", StringType()),
            StructField("recontact_date", DateType()),
            StructField("date_referee_agreed", DateType()),
            StructField("referee_used", StringType()),
            StructField("acquisition_process", StringType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class PartialPaymentTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "partial_payment"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("name", StringType()),
            StructField("currency_iso_code", StringType()),
            StructField("created_date", StringType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", StringType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", StringType()),
            StructField("last_activity_date", DateType()),
            StructField("invoice_reference", StringType()),
            StructField("amount", StringType()),
            StructField("credit_note_reference", StringType()),
            StructField("payment_date", StringType()),
            StructField("payment_method", StringType()),
            StructField("refund_id", StringType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
    

class PoaTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "poa"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("name", StringType()),
            StructField("currency_iso_code", StringType()),
            StructField("created_date", StringType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", StringType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", StringType()),
            StructField("last_activity_date", StringType()),
            StructField("principal_name", StringType(), metadata=masked_column_metadata),
            StructField("attorney_name", StringType(), metadata=masked_column_metadata),
            StructField("deactivation_date", BooleanType()),
            StructField("effective_date", StringType()),
            StructField("family_relation", BooleanType()),
            StructField("poa_status", StringType()),
            StructField("file_arrival_date", DateType()),
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
    

class RelationshipTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "relationship"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("name", StringType()),
            StructField("currency", StringType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("last_activity_date", DateType()),
            StructField("last_viewed_date", TimestampType()),
            StructField("last_referenced_date", TimestampType()),
            StructField("client_id", StringType()),
            StructField("provider", StringType()),
            StructField("integration_status", StringType()),
            StructField("integration_frequency", StringType()),
            StructField("data_source", StringType()),
            StructField("latest_statement_date", DateType()),
            StructField("latest_update_date", DateType()),
            StructField("last_updated_by", StringType()),
            StructField("relationship_balance", StringType()),
            StructField("integration_live_date", StringType()),
            StructField("primary_contact", StringType()),
            StructField("relationship_number", StringType()),
            StructField("filter_out", StringType()),
            StructField("non_integrated_stage", StringType()),
            StructField("date_provider_integrated", StringType()),
            StructField("update_frequency", StringType()),
            StructField("targeted_data_pipe", StringType()),
            StructField("data_pipe_setup_stage", StringType()),
            StructField("responsible_person", StringType()),
            StructField("inform_client_of_process_date", DateType()),
            StructField("client_to_contact_provider_date", DateType()),
            StructField("client_to_sign_loa_date", StringType()),
            StructField("ytree_send_information_to_provider_date", StringType()),
            StructField("provider_to_process_request_date", StringType()),
            StructField("client_to_link_accounts_via_ob_date", StringType()),
            StructField("done_date", DateType()),
            StructField("ytree_development_underway_date", StringType()),
            StructField("valid_data_pipe", StringType()),
            StructField("completed_valid_data_pipe", StringType()),
            StructField("date_of_pipe_added", StringType()),
            StructField("relationship_status", StringType()),
            StructField("oldest_statement_date", DateType()),
            StructField("minutes_to_update", StringType()),
            StructField("send_email_trigger", BooleanType()),
            StructField("expiry_date", DateType()),
            StructField("ownership", StringType()),
            StructField("relationship_manager", StringType()),
            StructField("related_accounts", StringType()),
            StructField("send_automated_chasers", BooleanType()),
            StructField("days_of_period_to_send", StringType()),
            StructField("frequency", StringType()),
            StructField("schedule_start_date", DateType()),
            StructField("next_scheduled_email_date", DateType()),
            StructField("client_name", StringType(), metadata=masked_column_metadata),
            StructField("rm_preferred_name", StringType(), metadata=masked_column_metadata),
            StructField("last_chaser_email_date", DateType()),
            StructField("bypass_validation", BooleanType()),
            StructField("follow_up_date", DateType()),
            StructField("do_not_contact", BooleanType()),
            StructField("loa_contact_email", StringType()),
            StructField("additional_contacts", StringType()),
            StructField("loa_accepted", BooleanType()),
            StructField("request_frequency", StringType()),
            StructField("selected_data_pipe", StringType()),
            StructField("account_stage", StringType()),
            StructField("notes", StringType()),
            StructField("provider_integrated", StringType()),
            StructField("relationship_notes", StringType()),
            StructField("is_internal_profile", BooleanType()),
            StructField("relationship_manager_email", StringType()),
            StructField("relationship_manager_name", StringType()),
            StructField("account_currency", StringType()),
            StructField("relationship_manager_email_mobile", StringType()),
            StructField("relationship_manager_name_mobile", StringType()),
            StructField("signed_loa_provider_forms", DateType()),
            StructField("autochaser_follow_up_count", FloatType()),
            StructField("automate_data_outreach", StringType()),
            StructField("copy_client_in_outreach_email", StringType()),
            StructField("data_outreach_secondary_email_address", StringType()),
            StructField("outreach_followup_date", DateType()),
            StructField("outreach_followup_required", BooleanType()),
            StructField("outreach_next_followup_date",  DateType()),
            StructField("valid_for", StringType()),
            StructField("signature_date", DateType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class ReferralTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "referral"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("owner_id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("name", StringType(), metadata=masked_column_metadata),
            StructField("currency", StringType()),
            StructField("record_type_id", StringType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("last_viewed_date", StringType()),
            StructField("last_referenced_date", StringType()),
            StructField("referred_lead", StringType()),
            StructField("stage", StringType()),
            StructField("referred_account", StringType()),
            StructField("account_referred_by", StringType()),
            StructField("referral_name", StringType(), metadata=masked_column_metadata),
            StructField("referred_by", StringType(), metadata=masked_column_metadata),
            StructField("in_progress_account_from_lead_referral", BooleanType()),
            StructField("referrer_name", StringType(), metadata=masked_column_metadata),
            StructField("active_account_from_lead_referral", BooleanType()),
            StructField("lead_referred_by", StringType()),
            StructField("referrals_first_meeting_date", StringType()),
            StructField("referrals_initial_analysis_date", StringType()),
            StructField("referrals_closing_date", StringType()),
            StructField("referrals_onboarding_date", StringType()),
            StructField("referrals_client_activation_date", StringType()),
            StructField("connection_stage", StringType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class TaskTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "task"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("parent_id", StringType()),
            StructField("activity_id", StringType()),
            StructField("created_by_id", StringType()),
            StructField("created_date", TimestampType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("from_name", StringType()),
            StructField("from_address", StringType()),
            StructField("validated_from_address", StringType()),
            StructField("to_address", StringType(), metadata=masked_column_metadata),
            StructField("cc_address", StringType(), metadata=masked_column_metadata),
            StructField("bcc_address", StringType(), metadata=masked_column_metadata),
            StructField("incoming", BooleanType()),
            StructField("has_attachment", BooleanType()),
            StructField("status", LongType()),
            StructField("message_date", TimestampType()),
            StructField("is_deleted", BooleanType()),
            StructField("reply_to_email_message_id", StringType()),
            StructField("is_externally_visible", BooleanType()),
            StructField("message_identifier", IntegerType()),
            StructField("thread_identifier", IntegerType()),
            StructField("is_client_managed", BooleanType()),
            StructField("related_to_id", IntegerType()),
            StructField("is_tracked", BooleanType()),
            StructField("is_opened", BooleanType()),
            StructField("first_opened_date", StringType()),
            StructField("last_opened_date", StringType()),
            StructField("is_bounced", BooleanType()),
            StructField("email_template_id", StringType()),
            StructField("recurrence_time_zone_sid_key", IntegerType()), 
            StructField("recurrence_type", IntegerType()), 
            StructField("recurrence_interval", IntegerType()), 
            StructField("recurrence_day_of_week_mask", IntegerType()), 
            StructField("recurrence_day_of_month", IntegerType()), 
            StructField("recurrence_instance", IntegerType()), 
            StructField("recurrence_month_of_year", IntegerType()), 
            StructField("recurrence_regenerated_type", IntegerType()), 
            StructField("task_subtype", StringType()), 
            StructField("completed_date_time", StringType()), 
            StructField("slscore_formatted_end_date_time", IntegerType()), 
            StructField("slscore_formatted_start_date_time", IntegerType()), 
            StructField("active_time_log", BooleanType()), 
            StructField("time_log_type", StringType()), 
            StructField("update_related_to", BooleanType()), 
            StructField("workflow_timer_formula", StringType()),
            StructField("who_id", StringType()),
            StructField("who_count", IntegerType()),
            StructField("what_id", StringType()),
            StructField("what_count", IntegerType()),
            StructField("activity_date", DateType()),
            StructField("subject", StringType(), metadata=masked_column_metadata),
            StructField("priority", StringType()),
            StructField("is_high_priority", BooleanType()),
            StructField("owner_id", StringType()),
            StructField("currency_iso_code", StringType()),
            StructField("type", StringType()),
            StructField("account_id", StringType()),
            StructField("is_closed", BooleanType()),
            StructField("is_archived", BooleanType()),
            StructField("call_duration_in_seconds", StringType()),
            StructField("call_type", StringType()),
            StructField("call_disposition", StringType()),
            StructField("call_object", StringType()),
            StructField("reminder_date_time", TimestampType()),
            StructField("is_reminder_set", BooleanType()),
            StructField("recurrence_activity_id", StringType()),
            StructField("is_recurrence", BooleanType()),
            StructField("recurrence_start_date_only", StringType()),
            StructField("recurrence_end_date_only", StringType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class UserTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "user"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("username", StringType(), metadata=masked_column_metadata),
            StructField("last_name", StringType(), metadata=masked_column_metadata),
            StructField("first_name", StringType(), metadata=masked_column_metadata),
            StructField("middle_name", StringType(), metadata=masked_column_metadata),
            StructField("name", StringType(), metadata=masked_column_metadata),
            StructField("company_name", StringType()), 
            StructField("division", StringType()), 
            StructField("department", StringType()),
            StructField("title", StringType(), metadata=masked_column_metadata),
            StructField("street", StringType(), metadata=masked_column_metadata),
            StructField("city", StringType(), metadata=masked_column_metadata),
            StructField("state", StringType(), metadata=masked_column_metadata),
            StructField("postal_code", StringType(), metadata=masked_column_metadata),
            StructField("country", StringType(), metadata=masked_column_metadata),
            StructField("latitude", StringType(), metadata=masked_column_metadata),
            StructField("longitude", StringType(), metadata=masked_column_metadata),
            StructField("geocode_accuracy", StringType(), metadata=masked_column_metadata),
            StructField("address", StringType(), metadata=masked_column_metadata),
            StructField("email", StringType(), metadata=masked_column_metadata),
            StructField("email_preferences_auto_bcc", BooleanType()), 
            StructField("email_preferences_auto_bcc_stay_in_touch", BooleanType()), 
            StructField("email_preferences_stay_in_touch_reminder", BooleanType()), 
            StructField("sender_email", StringType(), metadata=masked_column_metadata),
            StructField("sender_name", StringType(), metadata=masked_column_metadata),
            StructField("signature", StringType(), metadata=masked_column_metadata),
            StructField("stay_in_touch_subject", DoubleType()), 
            StructField("stay_in_touch_signature", DoubleType()), 
            StructField("stay_in_touch_note", DoubleType()), 
            StructField("phone", StringType(), metadata=masked_column_metadata),
            StructField("fax", StringType(), metadata=masked_column_metadata),
            StructField("mobile_phone", StringType(), metadata=masked_column_metadata),
            StructField("alias", StringType(), metadata=masked_column_metadata),
            StructField("community_nickname", StringType(), metadata=masked_column_metadata),
            StructField("badge_text", StringType()), 
            StructField("is_active", StringType()), 
            StructField("time_zone_sid_key", StringType()), 
            StructField("user_role_id", StringType()), 
            StructField("locale_sid_key", StringType()), 
            StructField("receives_info_emails", BooleanType()), 
            StructField("receives_admin_info_emails", BooleanType()), 
            StructField("email_encoding_key", StringType()), 
            StructField("default_currency_iso_code", StringType()), 
            StructField("currency_iso_code", StringType()), 
            StructField("profile_id", StringType()), 
            StructField("user_type", StringType()), 
            StructField("language_locale_key", StringType()), 
            StructField("employee_number", StringType(), metadata=masked_column_metadata),
            StructField("delegated_approver_id", DoubleType()), 
            StructField("manager_id", StringType()), 
            StructField("last_login_date", StringType()), 
            StructField("last_password_change_date", StringType()), 
            StructField("created_date", StringType()), 
            StructField("created_by_id", StringType()), 
            StructField("last_modified_date", StringType()), 
            StructField("last_modified_by_id", StringType()), 
            StructField("system_modstamp", StringType()), 
            StructField("number_of_failed_logins", DoubleType()), 
            StructField("offline_trial_expiration_date", DoubleType()), 
            StructField("offline_pda_trial_expiration_date", DoubleType()), 
            StructField("user_permissions_marketing_user", BooleanType()), 
            StructField("user_permissions_offline_user", BooleanType()), 
            StructField("user_permissions_avantgo_user", BooleanType()), 
            StructField("user_permissions_call_center_auto_login", BooleanType()), 
            StructField("user_permissions_sf_content_user", BooleanType()), 
            StructField("user_permissions_interaction_user", BooleanType()), 
            StructField("user_permissions_support_user", BooleanType()), 
            StructField("forecast_enabled", BooleanType()), 
            StructField("user_preferences_activity_reminders_popup", BooleanType()), 
            StructField("user_preferences_event_reminders_checkbox_default", BooleanType()), 
            StructField("user_preferences_task_reminders_checkbox_default", BooleanType()), 
            StructField("user_preferences_reminder_sound_off", BooleanType()), 
            StructField("user_preferences_disable_all_feeds_email", BooleanType()), 
            StructField("user_preferences_disable_followers_email", BooleanType()), 
            StructField("user_preferences_disable_profile_post_email", BooleanType()), 
            StructField("user_preferences_disable_change_comment_email", BooleanType()), 
            StructField("user_preferences_disable_later_comment_email", BooleanType()), 
            StructField("user_preferences_dis_prof_post_comment_email", BooleanType()), 
            StructField("user_preferences_apex_pages_developer_mode", BooleanType()), 
            StructField("user_preferences_receive_no_notifications_as_approver", BooleanType()), 
            StructField("user_preferences_receive_notifications_as_delegated_approver", BooleanType()), 
            StructField("user_preferences_hide_csn_get_chatter_mobile_task", BooleanType()), 
            StructField("user_preferences_disable_mentions_post_email", BooleanType()), 
            StructField("user_preferences_dis_mentions_comment_email", BooleanType()), 
            StructField("user_preferences_hide_csn_desktop_task", BooleanType()), 
            StructField("user_preferences_hide_chatter_onboarding_splash", BooleanType()), 
            StructField("user_preferences_hide_second_chatter_onboarding_splash", BooleanType()), 
            StructField("user_preferences_dis_comment_after_like_email", BooleanType()), 
            StructField("user_preferences_disable_like_email", BooleanType()), 
            StructField("user_preferences_sort_feed_by_comment", BooleanType()), 
            StructField("user_preferences_disable_message_email", BooleanType()), 
            StructField("user_preferences_disable_bookmark_email", BooleanType()), 
            StructField("user_preferences_disable_share_post_email", BooleanType()), 
            StructField("user_preferences_enable_auto_sub_for_feeds", BooleanType()), 
            StructField("user_preferences_show_manager_to_external_users", BooleanType()), 
            StructField("user_preferences_show_email_to_external_users", BooleanType()), 
            StructField("user_preferences_show_work_phone_to_external_users", BooleanType()), 
            StructField("user_preferences_show_mobile_phone_to_external_users", BooleanType()), 
            StructField("user_preferences_show_fax_to_external_users", BooleanType()), 
            StructField("user_preferences_show_street_address_to_external_users", BooleanType()), 
            StructField("user_preferences_show_city_to_external_users", BooleanType()), 
            StructField("user_preferences_show_state_to_external_users", BooleanType()), 
            StructField("user_preferences_show_postal_code_to_external_users", BooleanType()), 
            StructField("user_preferences_show_country_to_external_users", BooleanType()), 
            StructField("user_preferences_show_profile_pic_to_guest_users", BooleanType()), 
            StructField("user_preferences_show_title_to_guest_users", BooleanType()), 
            StructField("user_preferences_show_city_to_guest_users", BooleanType()), 
            StructField("user_preferences_show_state_to_guest_users", BooleanType()), 
            StructField("user_preferences_show_postal_code_to_guest_users", BooleanType()), 
            StructField("user_preferences_show_country_to_guest_users", BooleanType()), 
            StructField("user_preferences_hide_invoices_redirect_confirmation", BooleanType()), 
            StructField("user_preferences_hide_statements_redirect_confirmation", BooleanType()), 
            StructField("user_preferences_hide_s1_browser_ui", BooleanType()), 
            StructField("user_preferences_disable_endorsement_email", BooleanType()), 
            StructField("user_preferences_path_assistant_collapsed", BooleanType()), 
            StructField("user_preferences_cache_diagnostics", BooleanType()), 
            StructField("user_preferences_show_email_to_guest_users", BooleanType()), 
            StructField("user_preferences_show_manager_to_guest_users", BooleanType()), 
            StructField("user_preferences_show_work_phone_to_guest_users", BooleanType()), 
            StructField("user_preferences_show_mobile_phone_to_guest_users", BooleanType()), 
            StructField("user_preferences_show_fax_to_guest_users", BooleanType()), 
            StructField("user_preferences_show_street_address_to_guest_users", BooleanType()), 
            StructField("user_preferences_lightning_experience_preferred", BooleanType()), 
            StructField("user_preferences_preview_lightning", BooleanType()), 
            StructField("user_preferences_hide_end_user_onboarding_assistant_modal", BooleanType()), 
            StructField("user_preferences_hide_lightning_migration_modal", BooleanType()), 
            StructField("user_preferences_hide_sfx_welcome_mat", BooleanType()), 
            StructField("user_preferences_hide_bigger_photo_callout", BooleanType()), 
            StructField("user_preferences_global_nav_grid_menu_wt_shown", BooleanType()), 
            StructField("user_preferences_create_lex_apps_wt_shown", BooleanType()), 
            StructField("user_preferences_favorites_wt_shown", BooleanType()), 
            StructField("user_preferences_record_home_section_collapse_wt_shown", BooleanType()), 
            StructField("user_preferences_record_home_reserved_wt_shown", BooleanType()), 
            StructField("user_preferences_favorites_show_top_favorites", BooleanType()), 
            StructField("user_preferences_exclude_mail_app_attachments", BooleanType()), 
            StructField("user_preferences_suppress_task_sfx_reminders", BooleanType()), 
            StructField("user_preferences_suppress_event_sfx_reminders", BooleanType()), 
            StructField("user_preferences_preview_custom_theme", BooleanType()), 
            StructField("user_preferences_has_celebration_badge", BooleanType()), 
            StructField("user_preferences_user_debug_mode_pref", BooleanType()), 
            StructField("user_preferences_srh_override_activities", BooleanType()), 
            StructField("user_preferences_new_lightning_report_run_page_enabled", BooleanType()), 
            StructField("user_preferences_native_email_client", BooleanType()), 
            StructField("user_preferences_hide_browse_product_redirect_confirmation", BooleanType()), 
            StructField("user_preferences_hide_legacy_retirement_modal", BooleanType()),
            StructField("user_preferences_disable_file_share_notifications_for_api", BooleanType()),
            StructField("user_preferences_show_title_to_external_users", BooleanType()),
            StructField("user_preferences_global_nav_bar_wt_shown", BooleanType()),
            StructField("contact_id", DoubleType()),
            StructField("account_id", DoubleType()), 
            StructField("call_center_id", DoubleType()), 
            StructField("extension", DoubleType()), 
            StructField("federation_identifier", DoubleType()), 
            StructField("about_me", StringType(), metadata=masked_column_metadata),
            StructField("full_photo_url", StringType()), 
            StructField("small_photo_url", StringType()), 
            StructField("is_ext_indicator_visible", BooleanType()), 
            StructField("out_of_office_message", StringType()), 
            StructField("medium_photo_url", StringType()), 
            StructField("digest_frequency", StringType()),
            StructField("default_group_notification_frequency", StringType()), 
            StructField("last_viewed_date", StringType()), 
            StructField("last_referenced_date", StringType()), 
            StructField("banner_photo_url", StringType()), 
            StructField("small_banner_photo_url", StringType()), 
            StructField("medium_banner_photo_url", StringType()), 
            StructField("is_profile_photo_active", BooleanType()), 
            StructField("individual_id", DoubleType()), 
            StructField("expected_client_interaction_hours", DoubleType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class TnCsTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "tncs"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("name", StringType()),
            StructField("currency_iso_code", StringType()),
            StructField("created_date", StringType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("signed_by", StringType()),
            StructField("key", StringType()),
            StructField("requested_date", DateType()),
            StructField("signed_date", DateType()),
            StructField("signed_for", StringType()),
            StructField("version", StringType()),
            StructField("replaces_paper_t_cs", BooleanType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class KycTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "kyc"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("name", StringType()),
            StructField("currency_iso_code", StringType()),
            StructField("record_type_id", StringType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("last_activity_date", DateType()),
            StructField("account", StringType()),
            StructField("approval_date", DateType()),
            StructField("google_search_complete_date", DateType()),
            StructField("google_search_findings", StringType(), metadata=masked_column_metadata),
            StructField("is_pep", BooleanType()),
            StructField("po_a_expiry_date", DateType()),
            StructField("po_i_expiry_date", DateType()),
            StructField("primary_source_of_funds", StringType()),
            StructField("source_of_funds_details", StringType(), metadata=masked_column_metadata),
            StructField("stage", StringType()),
            StructField("source_of_wealth", StringType(), metadata=masked_column_metadata),
            StructField("primary_source_of_wealth", StringType()),
            StructField("source_of_wealth_details", StringType(), metadata=masked_column_metadata),
            StructField("source_of_funds", StringType(), metadata=masked_column_metadata),
            StructField("applicant_record_link", StringType(), metadata=masked_column_metadata),
            StructField("is_re_kyc_complete", BooleanType()),
            StructField("is_kyc_automated_expiry_email_sent", BooleanType()),
            StructField("is_kyc_automated_reminder_i_email_sent", BooleanType()),
            StructField("is_kyc_automated_reminder_ii_email_sent", BooleanType()),
            StructField("is_kyc_automated_reminder_iii_email_sent", BooleanType()),
            StructField("is_kyc_automated_reminder_iv_email_sent", BooleanType()),
            StructField("kyc_automated_expiry_notification_date", DateType()),
            StructField("is_send_email_due_today", BooleanType()),
            StructField("kyc_automated_expiry_reminder_i_date", DateType()),
            StructField("kyc_automated_expiry_reminder_ii_date", DateType()),
            StructField("kyc_automated_expiry_reminder_iii_date", DateType()),
            StructField("kyc_automated_expiry_reminder_iv_date", DateType()),
            StructField("manual_kyc_requested", BooleanType()),
            StructField("account_record_type", StringType()),
            StructField("bac_decision_date", DateType()),
            StructField("bac_decision_details", StringType()),
            StructField("kyc_risk_level", StringType()),
            StructField("kyc_risk_score", DoubleType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class ProviderTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "provider"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"
        self.data_lineage = get_data_lineage(self.table_name)

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("owner_id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("name", StringType()),
            StructField("currency_iso_code", StringType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("last_viewed_date", TimestampType()),
            StructField("last_referenced_date", TimestampType()),
            StructField("primary_provider_contact", StringType()),
            StructField("notes", StringType()),
            StructField("integrated", StringType()),
            StructField("date_integrated", DateType()),
            StructField("target_data_pipe", StringType()),
            StructField("open_banking", StringType()),
            StructField("open_banking_relationships", DoubleType()),
            StructField("api", BooleanType()),
            StructField("adviser_portal_manual", BooleanType()),
            StructField("adviser_portal_scrape", BooleanType()),
            StructField("auto_chased_provider", BooleanType()),
            StructField("integration_contact_email", StringType()),
            StructField("loa_contact_email", StringType()),
            StructField("loa_link", StringType()),
            StructField("loa_type", StringType()),
            StructField("manually_chased_provider", BooleanType()),
            StructField("open_banking2", BooleanType()),
            StructField("postal_address", StringType()),
            StructField("sftp", BooleanType()),
            StructField("sla_turnaround_time_days", DoubleType()),
            StructField("send_loa_via", StringType()),
            StructField("signature_required", StringType()),
            StructField("data_pipe_validation_flag", BooleanType()),
            StructField("information_only_portal", BooleanType()),
            StructField("loa_not_required", BooleanType()),
            StructField("provider_does_not_accept_loa", BooleanType()),
            StructField("relationship_manager_required", BooleanType()),
            StructField("client_update", BooleanType()),
            StructField("visible_to_all_clients", BooleanType()),
            StructField("account_number_required", BooleanType()),
            StructField("country", StringType()),
            StructField("city", StringType()),
            StructField("postcode", StringType()),
            StructField("state_province", StringType()),
            StructField("street_address", StringType()),
            StructField("third_party_loa_generation", StringType()),
            StructField("third_party_provider_id", StringType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""


class TotalBillableAssetTable(TablesDynamic):

    def __init__(self):
        self.file_tag = "total_billable_asset"
        self.table_name = f"{db_name}.{self.file_tag}"
        self.hive_table_name = f"{self.table_name}_all"

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("is_deleted", BooleanType()),
            StructField("name", StringType()),
            StructField("currency_iso_code", StringType()),
            StructField("created_date", TimestampType()),
            StructField("created_by_id", StringType()),
            StructField("last_modified_date", TimestampType()),
            StructField("last_modified_by_id", StringType()),
            StructField("system_modstamp", TimestampType()),
            StructField("account", StringType()),
            StructField("value", DoubleType()),
            StructField("daily_change", DoubleType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
