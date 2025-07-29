# Databricks notebook source
from typing import Tuple
import os
import re
import traceback
import pandas as pd
from datetime import datetime

from pyspark.sql import SparkSession

from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

from data_science.lead_prediction.df_utils.data_fetch import (
    column_names_definition as col_def, queries, common_fcns as fcns
)

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/data_fetch.py"


def get_source_dfs(spark: SparkSession):
    d = """select * from hive_metastore.salesforce.lead_all"""
    df1 = spark.sql(d)
    df1 = df1.toPandas()
    d1 = """select * from hive_metastore.salesforce.opportunity_all"""
    df2 = spark.sql(d1)
    d2 = """select * from hive_metastore.salesforce.company_all"""
    df3 = spark.sql(d2)
    d3 = """select * from hive_metastore.salesforce.account_all"""
    df4 = spark.sql(d3)

    col_names = df1.columns
    formatted_column_names = '[' + ', '.join([f'"{col}"' for col in col_names]) + ']'
    # print(formatted_column_names)
    col_names2 = df2.columns
    formatted_column_names2 = '[' + ', '.join([f'"{col}"' for col in col_names2]) + ']'
    # print(formatted_column_names2)
    col_names3 = df3.columns
    formatted_column_names3 = '[' + ', '.join([f'"{col}"' for col in col_names3]) + ']'
    # print(formatted_column_names3)
    col_names4 = df4.columns
    formatted_column_names4 = '[' + ', '.join([f'"{col}"' for col in col_names4]) + ']'
    # print(formatted_column_names4)

    return


# Function to generate unique column aliases
def generate_unique_aliases(columns, table_alias):
    unique_aliases = []
    counter = 1
    for col in columns:
        unique_aliases.append(f"{col}_{table_alias}")
        counter += 1
    return unique_aliases


def create_final_select_clause():
    # Generate unique column aliases for each table
    unique_aliases_table1 = generate_unique_aliases(col_def.table1_columns_lead_all, "lead_tbl")
    unique_aliases_table2 = generate_unique_aliases(col_def.table2_columns_opp_all, "opp_tbl")
    unique_aliases_table3 = generate_unique_aliases(col_def.table3_columns_company_all, "company_tbl")
    unique_aliases_table4 = generate_unique_aliases(col_def.table4_columns_account_all, "account_tbl")

    # Create SELECT clauses with column renaming for each table
    select_clause_table1 = ",\n".join(
        [f"t1.{col} AS {alias}" for col, alias in zip(col_def.table1_columns_lead_all, unique_aliases_table1)])
    select_clause_table2 = ",\n".join(
        [f"t2.{col} AS {alias}" for col, alias in zip(col_def.table2_columns_opp_all, unique_aliases_table2)])
    select_clause_table3 = ",\n".join(
        [f"t3.{col} AS {alias}" for col, alias in zip(col_def.table3_columns_company_all, unique_aliases_table3)])
    select_clause_table4 = ",\n".join(
        [f"t4.{col} AS {alias}" for col, alias in zip(col_def.table4_columns_account_all, unique_aliases_table4)])

    # Create the final SELECT clause combining both table clauses
    select_clause = f"{select_clause_table1},\n{select_clause_table2},\n{select_clause_table3},\n{select_clause_table4}"

    # from hive_metastore.salesforce.lead_all as t1
    #   FULL OUTER JOIN hive_metastore.salesforce.opportunity_all as t2 on t1.converted_opportunity_id=t2.id
    #   FULL OUTER JOIN hive_metastore.salesforce.company_all as t3 on t1.primary_employer2 = t3.id
    #   FULL OUTER JOIN hive_metastore.salesforce.account_all as t4 on t1.converted_account_id = t4.id
    # where t1.internal_user_profile is not true

    return select_clause


def build_query(select_clause: str):
    # Building query
    return queries.construct_select_clause_query(select_clause)


def get_query_pd_df(spark: SparkSession, query: str) -> pd.DataFrame:
    dfs = spark.sql(query)
    dfs_to_pandas = dfs.toPandas()
    df = dfs_to_pandas.copy()
    df.dropna(axis=1, how='all', inplace=True)
    # display(df)

    return df


def drop_missing_pd_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    exception_columns = col_def.exception_columns
    missing_columns = df.columns[
        (100 * (df.isnull().sum() / len(df.index)) > 70) & (~df.columns.isin(exception_columns))
    ]

    df = df.drop(missing_columns, axis=1)

    return df


# Function to extract the date part from datetime values
def extract_date(value):
    try:
        # Split the string using 'T' as the delimiter and return the date part
        return value.split('T')[0]
    except AttributeError:
        return value
    except IndexError:
        # Handle cases where the delimiter 'T' is not found in the string
        return value


# Function to check if a value matches valid date formats
def is_valid_date_format(value):
    # Convert the value to a string
    value_str = str(value)
    # Replace "Z" with an empty string before checking the format
    value_str = value_str.replace('Z', '')
    # Define regular expressions for various date formats
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    # datetime_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$'
    # iso8601_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?\+\d{4}$'
    datetime_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z?$'
    iso8601_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?\+?\d{4}$'

    # Convert the value to a string and check if it matches any of the specified patterns
    return (
            bool(re.match(date_pattern, str(value))) or
            bool(re.match(datetime_pattern, str(value))) or
            bool(re.match(iso8601_pattern, str(value)))
    )


def cast_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Identify object columns with valid date values
    date_columns = [
                       col for col in df.select_dtypes(include=['object']).columns
                       if not df[col].dropna().empty and is_valid_date_format(df[col].dropna().iloc[0])
                   ] + ['created_date_opp_tbl', 'last_modified_date_opp_tbl', 'system_modstamp_opp_tbl',
                        'email_bounced_date_lead_tbl', 'created_date_company_tbl', 'last_modified_date_company_tbl',
                        'system_modstamp_company_tbl', 'created_date_lead_tbl', 'last_modified_date_lead_tbl',
                        'system_modstamp_lead_tbl']

    # print(date_columns)
    # Convert identified columns to datetime and fill null values with '1800-01-01'
    for col in date_columns:
        # Extract the date part and convert it to datetime
        df[col] = pd.to_datetime(df[col].apply(extract_date), errors='coerce').fillna(pd.to_datetime('1800-01-01'))
        # print(df[col])

    return df


# Function to check if a value is boolean-like
def is_boolean_like(val):
    if isinstance(val, str):
        val_lower = val.strip().lower()
        return val_lower in ['true', 'false']
    elif isinstance(val, bool):
        return True
    return False


def cast_boolean_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Identify object columns
    object_columns = df.select_dtypes(include=['object']).columns

    # Identify potential boolean columns with 'TRUE' and 'FALSE' values (case-insensitive),
    # as well as Python boolean values (True and False)
    potential_boolean_columns = []
    for col in object_columns:
        non_null_values = df[col].dropna()

        # Skip columns with all null values
        if non_null_values.empty:
            continue

        # Calculate the percentage of boolean-like values
        boolean_like_count = sum(1 for val in non_null_values if is_boolean_like(val))
        total_count = len(non_null_values)

        # Check if 99% or more of the values are boolean-like
        if boolean_like_count / total_count >= 0.99:
            potential_boolean_columns.append(col)

    # Print the list of potential boolean columns
    print("Potential boolean columns:", potential_boolean_columns)

    # Convert identified potential boolean columns to boolean data type
    for col in potential_boolean_columns:
        df[col] = df[col].apply(
            # lambda x: x.strip().lower() == 'true' if isinstance(x, str) and pd.notna(x) else x
            lambda x: x.strip().lower() == 'true' if isinstance(x, str) and pd.notna(x) else False
        ).astype(bool)

        # Print the column name and data for each potential boolean column
        # print(f"Column: {col}")
        # print(df[col])

    return df


def cast_integer_and_float_columns(df: pd.DataFrame) -> pd.DataFrame:
    df1 = df.copy()
    # Identify object columns
    object_columns = df1.select_dtypes(include=['object']).columns

    # Initialize empty lists to store integer and float columns
    integer_columns = []
    float_columns = []

    # Iterate through object columns and check for integer and float values
    for col in object_columns:
        non_null_values = df1[col].dropna()

        if non_null_values.empty:
            continue

        # Try converting non-null values to integers
        try:
            non_null_values.apply(lambda x: int(x) if x != 'null' else x)
            integer_columns.append(col)
        except ValueError:
            # If conversion to int fails, try converting to float
            try:
                non_null_values.apply(lambda x: float(x) if x != 'null' else x)
                float_columns.append(col)
            except ValueError:
                pass
    float_columns.extend([
        'assets_available_in_multrees_gia_account_tbl',
        'assets_under_management_account_tbl',
        'total_billable_assets_account_tbl',
        'cash_available_in_multrees_gia_account_tbl', 'last_invoiced_amount_account_tbl',
        'days_between_analysis_complete_opp_tbl'
    ])
    # print("Integer columns:", integer_columns)
    # print("Float columns:", float_columns)

    for col in col_def.all_float_columns:
        df[col] = df[col].astype(float)

    return df


def pd_df_fillna(df: pd.DataFrame) -> pd.DataFrame:
    df5 = df.copy()
    df5['current_stage_lead_tbl'] = df5.apply(lambda row: 'Converted' if pd.isnull(row['current_stage_lead_tbl']) and not pd.isnull(row['id_opp_tbl']) else row['current_stage_lead_tbl'], axis=1)
    df5['current_stage_opp_tbl'] = df5.apply(lambda row: row['current_stage_lead_tbl'] if pd.notna(row['current_stage_lead_tbl']) and pd.isna(row['current_stage_opp_tbl']) else row['current_stage_opp_tbl'], axis=1)
    df5['id_lead_tbl'] = df5.apply(lambda row: row['id_opp_tbl'] if pd.notna(row['id_opp_tbl']) and pd.isna(row['id_lead_tbl']) else row['id_lead_tbl'], axis=1)
    df5.drop(columns=['id_opp_tbl'],inplace=True)
    mask = df5['account_source_account_tbl'].isnull()
    df5.loc[mask, 'account_source_account_tbl'] = df5.loc[mask, 'lead_source_lead_tbl']

    df5['stage_unqualified_date'] = df5['stage_unqualified_date'].fillna(df5['stage_qualified_date']).fillna(df5['stage_pitch_meeting_set_date']).fillna(df5['stage_converted_date']).fillna(df5['stage_initial_interaction_date']).fillna(df5['stage_initial_analysis_date']).fillna(df5['stage_qa_meeting_date']).fillna(df5['stage_statement_gathering_date']).fillna(df5['stage_hcls_prep_date']).fillna(df5['stage_health_check_meeting_date']).fillna(df5['stage_closing_date']).fillna(df5['stage_on_boarding_date']).fillna(df5['stage_complete_date'])

    df5['stage_qualified_date'] = df5['stage_qualified_date'].fillna(df5['stage_pitch_meeting_set_date']).fillna(df5['stage_converted_date']).fillna(df5['stage_initial_interaction_date']).fillna(df5['stage_initial_analysis_date']).fillna(df5['stage_qa_meeting_date']).fillna(df5['stage_statement_gathering_date']).fillna(df5['stage_hcls_prep_date']).fillna(df5['stage_health_check_meeting_date']).fillna(df5['stage_closing_date']).fillna(df5['stage_on_boarding_date']).fillna(df5['stage_complete_date'])

    df5['stage_pitch_meeting_set_date'] = df5['stage_pitch_meeting_set_date'].fillna(df5['stage_converted_date']).fillna(df5['stage_initial_interaction_date']).fillna(df5['stage_initial_analysis_date']).fillna(df5['stage_qa_meeting_date']).fillna(df5['stage_statement_gathering_date']).fillna(df5['stage_hcls_prep_date']).fillna(df5['stage_health_check_meeting_date']).fillna(df5['stage_closing_date']).fillna(df5['stage_on_boarding_date']).fillna(df5['stage_complete_date'])

    df5['stage_converted_date'] = df5['stage_converted_date'].fillna(df5['stage_initial_interaction_date']).fillna(df5['stage_initial_analysis_date']).fillna(df5['stage_qa_meeting_date']).fillna(df5['stage_statement_gathering_date']).fillna(df5['stage_hcls_prep_date']).fillna(df5['stage_health_check_meeting_date']).fillna(df5['stage_closing_date']).fillna(df5['stage_on_boarding_date']).fillna(df5['stage_complete_date'])

    return df5


def run_num_days_calculations(df5: pd.DataFrame) -> pd.DataFrame:
    df6 = df5.copy()

    df6['no_of_days_in_stage'] = df6['days_in_current_stage_opp_tbl'].apply(
        lambda x: float(re.search(r'\d+', x).group()) if pd.notnull(x) else None)
    # Fill null values in no_of_days_in_stage with values from days_in_stage_lead_tbl
    df6['no_of_days_in_stage'].fillna(df6['days_in_stage_lead_tbl'], inplace=True)
    df6['no_of_days_in_stage'].fillna(-1, inplace=True)
    df6['no_of_days_in_stage'] = df6['no_of_days_in_stage'].astype(int)

    df6['stage_qualified_date'] = pd.to_datetime(df6['stage_qualified_date'])
    df6['stage_unqualified_date'] = pd.to_datetime(df6['stage_unqualified_date'])
    df6['no_of_days_in_stage_unqualified_date'] = df6.apply(fcns.calculate_no_of_days_1, axis=1)

    df6['stage_pitch_meeting_set_date'] = pd.to_datetime(df6['stage_pitch_meeting_set_date'])
    df6['stage_qualified_date'] = pd.to_datetime(df6['stage_qualified_date'])
    df6['no_of_days_in_stage_qualified_date'] = df6.apply(fcns.calculate_no_of_days_2, axis=1)

    df6['stage_converted_date'] = pd.to_datetime(df6['stage_converted_date'])
    df6['stage_pitch_meeting_set_date'] = pd.to_datetime(df6['stage_pitch_meeting_set_date'])
    df6['no_of_days_in_stage_pitch_meeting_set_date'] = df6.apply(fcns.calculate_no_of_days_3, axis=1)

    df6['stage_converted_date'] = pd.to_datetime(df6['stage_converted_date'])
    df6['stage_initial_interaction_date'] = pd.to_datetime(df6['stage_initial_interaction_date'])
    df6['no_of_days_in_stage_converted_date'] = df6.apply(fcns.calculate_no_of_days_4, axis=1)

    df6['stage_converted_date'] = pd.to_datetime(df6['stage_converted_date'])
    df6['stage_initial_interaction_date'] = pd.to_datetime(df6['stage_initial_interaction_date'])
    df6['no_of_days_in_stage_converted_date'] = df6.apply(fcns.calculate_no_of_days_5, axis=1)

    df6['stage_initial_interaction_date'] = pd.to_datetime(df6['stage_initial_interaction_date'])
    df6['stage_initial_analysis_date'] = pd.to_datetime(df6['stage_initial_analysis_date'])
    df6['no_of_days_in_stage_initial_interaction_date'] = df6.apply(fcns.calculate_no_of_days_6, axis=1)

    df6['stage_initial_analysis_date'] = pd.to_datetime(df6['stage_initial_analysis_date'])
    df6['stage_qa_meeting_date'] = pd.to_datetime(df6['stage_qa_meeting_date'])
    df6['no_of_days_in_stage_initial_analysis_date'] = df6.apply(fcns.calculate_no_of_days_7, axis=1)

    df6['stage_qa_meeting_date'] = pd.to_datetime(df6['stage_qa_meeting_date'])
    df6['stage_statement_gathering_date'] = pd.to_datetime(df6['stage_statement_gathering_date'])
    df6['no_of_days_in_stage_qa_meeting_date'] = df6.apply(fcns.calculate_no_of_days_8, axis=1)

    df6['stage_statement_gathering_date'] = pd.to_datetime(df6['stage_statement_gathering_date'])
    df6['stage_hcls_prep_date'] = pd.to_datetime(df6['stage_hcls_prep_date'])
    df6['no_of_days_in_stage_statement_gathering_date'] = df6.apply(fcns.calculate_no_of_days_9, axis=1)

    df6['stage_health_check_meeting_date'] = pd.to_datetime(df6['stage_health_check_meeting_date'])
    df6['stage_hcls_prep_date'] = pd.to_datetime(df6['stage_hcls_prep_date'])
    df6['no_of_days_in_stage_hcls_prep_date'] = df6.apply(fcns.calculate_no_of_days_10, axis=1)

    df6['stage_health_check_meeting_date'] = pd.to_datetime(df6['stage_health_check_meeting_date'])
    df6['stage_closing_date'] = pd.to_datetime(df6['stage_closing_date'])
    df6['no_of_days_in_stage_health_check_meeting_date'] = df6.apply(fcns.calculate_no_of_days_11, axis=1)

    df6['stage_on_boarding_date'] = pd.to_datetime(df6['stage_on_boarding_date'])
    df6['stage_closing_date'] = pd.to_datetime(df6['stage_closing_date'])
    df6['no_of_days_in_stage_closing_date'] = df6.apply(fcns.calculate_no_of_days_12, axis=1)

    df6['stage_on_boarding_date'] = pd.to_datetime(df6['stage_on_boarding_date'])
    df6['stage_complete_date'] = pd.to_datetime(df6['stage_complete_date'])
    df6['no_of_days_in_stage_on_boarding_date'] = df6.apply(fcns.calculate_no_of_days_13, axis=1)

    #
    object_columns1 = ['id_lead_tbl', 'salutation_lead_tbl', 'primary_employer_lead_tbl',
                       'estimated_investable_assets_from_website_lead_tbl', 'current_stage_opp_tbl', 'name_company_tbl',
                       'industry_company_tbl', 'account_source_account_tbl', 'domicile_account_tbl',
                       'tax_residency_account_tbl', 'us_connected_person_account_tbl', 'occupation_lead_tbl']
    # object_columns = df5.select_dtypes(include=['object']).columns
    # df6 = df6.drop(columns=set(object_columns) - set(object_columns1))
    # df6 = df6[df6['current_stage_opp_tbl'] != 'Converted']

    return df6


def total_days_stage_mapping(df6: pd.DataFrame) -> pd.DataFrame:
    df7 = df6.copy()

    stage_mapping = {
        'Initial Interaction': 0,
        'Initial Analysis': 1,
        'Q&A Meeting': 2,
        'Statement gathering': 3,
        'HC/LS prep': 4,
        'Health check meeting': 5,
        'Closing': 6,
        'On-boarding': 7,
        'Complete': 8,
        'Cold': 9,
        'On Hold': 10,
        'Converted': 11

    }

    # Create a new column with the numerical values
    df7['current_stage_opp_tbl_encoded'] = df7['current_stage_opp_tbl'].map(stage_mapping).astype(int)

    columns_to_sum = ['no_of_days_in_stage_unqualified_date',
                      'no_of_days_in_stage_qualified_date',
                      'no_of_days_in_stage_pitch_meeting_set_date',
                      'no_of_days_in_stage_converted_date',
                      'no_of_days_in_stage_initial_interaction_date',
                      'no_of_days_in_stage_initial_analysis_date',
                      'no_of_days_in_stage_qa_meeting_date',
                      'no_of_days_in_stage_statement_gathering_date',
                      'no_of_days_in_stage_hcls_prep_date',
                      'no_of_days_in_stage_health_check_meeting_date',
                      'no_of_days_in_stage_closing_date',
                      'no_of_days_in_stage_on_boarding_date']

    df7['total_days'] = df7[columns_to_sum].apply(lambda row: sum(val if val != -1 else 0 for val in row), axis=1)

    return df7


def rename_pd_df_columns(df7: pd.DataFrame) -> pd.DataFrame:
    new_column_names = []
    for col in df7.columns:
        if col.startswith('y_tree'):
            new_column_names.append('y_' + col[6:])
        else:
            new_column_names.append(col)

    df7 = df7.rename(columns=dict(zip(df7.columns, new_column_names)))

    new_df = df7[col_def.selected_col]

    return new_df


def write_df_to_dbfs(new_df: pd.DataFrame):
    today_date = datetime.today().strftime('%B_%m%d%Y')

    # Create the file name
    file_name = f"{today_date}.csv"
    # print(file_name)
    path = "/dbfs/FileStore/Lead_Pred_test"
    file_path_csv = f"{path}/{file_name}"
    new_df.to_csv(file_path_csv, index=False, mode='w')
    print(f"\nnew_df written to : {path}/{file_path_csv}\n")


def data_fetch_steps(spark: SparkSession):
    # get_source_dfs(spark)
    select_clause = create_final_select_clause()
    query = build_query(select_clause)
    df = get_query_pd_df(spark, query)
    df = drop_missing_pd_df_columns(df)
    df = cast_date_columns(df)
    df = cast_boolean_columns(df)
    df = cast_integer_and_float_columns(df)
    df = pd_df_fillna(df)
    df = run_num_days_calculations(df)
    df = total_days_stage_mapping(df)
    df = rename_pd_df_columns(df)
    write_df_to_dbfs(df)


@log_general_info(
    env=locals(),
    etl_data="data_science__lead_prediction__data_fetch",
    script_path=script_path,
    data_sources_type="lakehouse"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    data_source_n_status = []

    logger_helper = LoggerHelper(source="")
    try:
        data_fetch_steps(spark)
        logger_helper.log_status()

    except Exception as e:
        msg = f"Error running data_fetch:\n{traceback.format_exc()}"
        logger_helper.log_status(traceback=msg, failed=True)

    data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())
