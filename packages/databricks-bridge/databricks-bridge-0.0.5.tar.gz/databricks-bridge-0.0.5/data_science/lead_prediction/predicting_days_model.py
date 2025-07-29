# Databricks notebook source
from typing import Tuple
import os
import traceback
import pandas as pd
import numpy as np
from datetime import datetime

from pyspark.sql import SparkSession
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor
import joblib

from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

from data_science.lead_prediction.df_utils.predicting_days_model import column_names_definition as col_def

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/predicting_days_model.py"

today_date = datetime.today().strftime('%B_%m%d%Y')
# Create the file name
file_name = f"{today_date}.csv"
# file_name='May_05022024.csv'
print(file_name)
path = f"/dbfs/FileStore/Lead_Pred_test"
source_files = []


def retrieve_source_df() -> pd.DataFrame:
    file_name_with_prefix = "LSTM_predictions_" + file_name
    print(f"\nretrieving file from: {path}/{file_name}\n")
    source_files.append(f"{path}/{file_name}")
    df = pd.read_csv(path+"/"+file_name)

    print(f"\nretrieving file from: {path}/{file_name_with_prefix}\n")
    source_files.append(f"{path}/{file_name_with_prefix}")
    final_stage_prediction = pd.read_csv(path+"/"+file_name_with_prefix)
    final_stage_prediction = final_stage_prediction[['id_lead_tbl', 'predicted_stage']]
    df = pd.merge(df, final_stage_prediction, on='id_lead_tbl', how='left')
    return df


def cast_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    # change date columns data type
    columns_to_change = col_def.columns_to_change
    for col in columns_to_change:
        df[col] = pd.to_datetime(df[col])

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # clean data
    df.loc[:, 'formatted_est_billable_assets_opp_tbl'] = \
    df['formatted_est_billable_assets_opp_tbl'].str.replace(',', '').str.split('.').str[0].fillna(0).astype(int)
    # df = df[(df['current_stage_opp_tbl_encoded'] < 11)]

    return df


def handle_outliers(df: pd.DataFrame) -> pd.DataFrame:
    # handle outliers
    median_value = int(
        df.loc[
            df['no_of_days_in_stage_initial_interaction_date'] <= 105,
            'no_of_days_in_stage_initial_interaction_date'].median()
    )
    df.loc[
        df['no_of_days_in_stage_initial_interaction_date'] > 105,
        'no_of_days_in_stage_initial_interaction_date'
    ] = median_value

    median_value = int(
        df.loc[
            df['no_of_days_in_stage_initial_analysis_date'] <= 155,
            'no_of_days_in_stage_initial_analysis_date'].median()
    )

    df.loc[
        df['no_of_days_in_stage_initial_analysis_date'] > 155,
        'no_of_days_in_stage_initial_analysis_date'
    ] = median_value

    median_value = int(
        df.loc[df['no_of_days_in_stage_qa_meeting_date'] <= 65, 'no_of_days_in_stage_qa_meeting_date'].median()
    )

    df.loc[df['no_of_days_in_stage_qa_meeting_date'] > 65, 'no_of_days_in_stage_qa_meeting_date'] = median_value

    median_value = int(
        df.loc[df['no_of_days_in_stage_closing_date'] <= 250, 'no_of_days_in_stage_closing_date'].median()
    )

    df.loc[df['no_of_days_in_stage_closing_date'] > 250, 'no_of_days_in_stage_closing_date'] = median_value

    median_value = int(
        df.loc[df['no_of_days_in_stage_on_boarding_date'] <= 50, 'no_of_days_in_stage_on_boarding_date'].median()
    )

    df.loc[df['no_of_days_in_stage_on_boarding_date'] > 50, 'no_of_days_in_stage_on_boarding_date'] = median_value

    return df


def run_last_stage_date_calculations(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # get 'last_stage_number', 'last_stage_days', 'first_to_last'
    null_date = pd.to_datetime('1800-01-01 00:00:00+00:00')
    max_date = df['last_modified_date_opp_tbl'].max()

    def assign_last_stage(row):
        stages = [
            'stage_closing_date',
            'stage_health_check_meeting_date',
            'stage_hcls_prep_date',
            'stage_statement_gathering_date',
            'stage_qa_meeting_date',
            'stage_initial_analysis_date',
            'stage_initial_interaction_date',
            'stage_converted_date',
            'stage_pitch_meeting_set_date',
            'stage_qualified_date',
            'stage_unqualified_date'
        ]

        current_stage = 'stage_on_boarding_date'
        last_stage_number = 12
        for previous_stage in stages:
            last_stage_number = last_stage_number - 1
            if (row[current_stage] != null_date):
                last_stage_date = row[current_stage]
                last_stage_days = (row[current_stage] - row[previous_stage]).days
                if (last_stage_days < 0):
                    last_stage_days = 0
                total_days = (row[current_stage] - row['stage_unqualified_date']).days if (row[current_stage] - row[
                    'stage_unqualified_date']).days > 0 else (
                            row[current_stage] - row['stage_initial_interaction_date']).days
                # if(total_days > 365):
                #     total_days = 30
                return pd.Series({'last_stage_number': last_stage_number,
                                  'last_stage_date': last_stage_date,
                                  # 'last_stage_days': last_stage_days,
                                  'first_to_last': total_days
                                  })
            current_stage = previous_stage

    # df[['last_stage_number', 'last_stage_date', 'last_stage_days', 'total_days']] = df.apply(assign_last_stage, axis=1)
    df[['last_stage_number', 'last_stage_date', 'first_to_last']] = df.apply(assign_last_stage, axis=1)
    df_base = df.copy()

    return df, df_base


def apply_end_date(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # get days_to_end
    # get 'last_stage_number', 'last_stage_days', 'first_to_last'
    null_date = pd.to_datetime('1800-01-01 00:00:00+00:00')
    max_date = df['last_modified_date_opp_tbl'].max()

    def get_end_date(row):
        if (row['stage_complete_date'] != null_date):
            return pd.Series({'end_date': row['stage_complete_date']})
        elif (row['stage_cold_date_opp_tbl'] != null_date):
            return pd.Series({'end_date': row['stage_cold_date_opp_tbl']})
        elif (row['stage_on_hold_date_opp_tbl'] != null_date):
            return pd.Series({'end_date': row['stage_on_hold_date_opp_tbl']})
        else:
            return pd.Series({'end_date': max_date})

    df[['end_date']] = df.apply(get_end_date, axis=1)
    df['days_to_end'] = (df['end_date'] - df['last_stage_date']).dt.days
    df_base = df.copy()
    # df.to_csv('test.csv', index=False)

    return df, df_base


def transpose_pd_df(df: pd.DataFrame) -> pd.DataFrame:
    # unpivot
    numerical_columns = col_def.numerical_columns
    # [col for col in df.columns if any(substring in col for substring in columns_to_encode)]  +
    id_columns = col_def.id_columns

    df = pd.melt(df, id_vars=id_columns, value_vars=numerical_columns, var_name='stage', value_name='stage_value')
    id_columns_updated = col_def.id_columns_updated

    return df


def apply_stage_mapping(df: pd.DataFrame) -> pd.DataFrame:
    # mapping stages
    stage_mapping1 = {
        'no_of_days_in_stage_unqualified_date': 1,
        'no_of_days_in_stage_qualified_date': 2,
        'no_of_days_in_stage_pitch_meeting_set_date': 3,
        'no_of_days_in_stage_converted_date': 4,
        'no_of_days_in_stage_initial_interaction_date': 5,
        'no_of_days_in_stage_initial_analysis_date': 6,
        'no_of_days_in_stage_qa_meeting_date': 7,
        'no_of_days_in_stage_statement_gathering_date': 8,
        'no_of_days_in_stage_hcls_prep_date': 9,
        'no_of_days_in_stage_health_check_meeting_date': 10,
        'no_of_days_in_stage_closing_date': 11,
        'no_of_days_in_stage_on_boarding_date': 12,
    }
    df['stage'] = df['stage'].map(stage_mapping1).replace(np.nan, -1).astype(int)

    return df


# model helper
def create_X_and_y(df, y_column):
    X_list = df.columns
    X_list = [item for item in X_list if item not in (y_column)]
    X = df[X_list]
    y = df[y_column]#.values.ravel()
    return X, y


def separate_id_column(df):
    id_column = df['id_lead_tbl']
    columns_to_drop = ['id_lead_tbl']
    df = df.drop(columns=columns_to_drop)
    return df, id_column


def retrieve_training_pd_dfs(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # # create train and prod

    train = df[(df['stage_value'] >= 0) & ((df['current_stage_opp_tbl_encoded'] == 8))]
    prod = df[(df['stage_value'] < 0) & ((df['predicted_stage'] == 8))]

    column_to_drop = ['current_stage_opp_tbl_encoded', 'predicted_stage']
    train = train.drop(column_to_drop, axis=1)
    prod = prod.drop(column_to_drop, axis=1)

    return train, prod


def train_model(train: pd.DataFrame, prod: pd.DataFrame):
    # Initialize DataFrame
    df_prediction_group = pd.DataFrame()
    list_mae = []  # Initialize list for Mean Absolute Error
    list_mse = []  # Initialize list for Mean Squared Error

    # Initialize lists to store trained models and their filenames
    trained_models = []
    model_files = []

    # Train the model
    for stage_number in range(14):
        train_loop = train[(train['stage'] == stage_number)]
        prod_loop = prod[(prod['stage'] == stage_number)]

        if len(train_loop) <= 1 or len(prod_loop) <= 1:
            continue

        X, y = create_X_and_y(train_loop, 'stage_value')
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.8, random_state=42)
        X_prod, y_prod = create_X_and_y(prod_loop, 'stage_value')

        # Separate ID column if applicable
        X_train, train_id_column = separate_id_column(X_train)
        X_test, test_id_column = separate_id_column(X_test)
        X_prod, prod_id_column = separate_id_column(X_prod)

        # Train the model with specified hyperparameters
        model1 = RandomForestRegressor(bootstrap=True, max_depth=10, max_features='auto',
                                       min_samples_leaf=1, min_samples_split=2, n_estimators=100)
        model1.fit(X_train, y_train)

        # Make predictions and evaluate accuracy
        y_pred = model1.predict(X_test)
        y_pred = np.clip(y_pred, a_min=0, a_max=None)

        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)

        # Save the trained model
        model_file = f'model_{stage_number}_feb15_data.pkl'
        joblib.dump(model1, model_file)
        # model_files.append(model_file)

        # # Append trained model to list
        # trained_models.append(model1)

        # Make predictions on the production set
        prod_predictions = model1.predict(X_prod)
        prod_predictions = np.clip(prod_predictions, a_min=0, a_max=None)

        df_prediction_stage_days_prediction = pd.DataFrame(
            {'id_lead_tbl': prod_id_column, "stage_days_prediction": prod_predictions})
        df_prediction_stage_days_prediction['stage_number'] = stage_number

        list_mae = list_mae + [mae * len(df_prediction_group)]
        list_mse = list_mse + [mse * len(df_prediction_group)]
        df_prediction_group = pd.concat([df_prediction_group, df_prediction_stage_days_prediction], ignore_index=True)

    print("Print Mean Absolute Error: ", sum(list_mae) / len(df_prediction_group))
    print("Print Mean Squared Error: ", sum(list_mse) / len(df_prediction_group))

    print("Main shape: ", df_prediction_group.shape)
    print("Number of distinct values in 'id_lead_tbl' column:", df_prediction_group['id_lead_tbl'].nunique())

    df_prediction_group = df_prediction_group.groupby('id_lead_tbl')['stage_days_prediction'].sum().reset_index()
    df_prediction_group.columns = ['id_lead_tbl', 'remaining_days_prediction']

    return df_prediction_group


def apply_predicted_date(df_base: pd.DataFrame, df_prediction_group: pd.DataFrame) -> pd.DataFrame:
    df_complete_date_prediction = pd.merge(df_base, df_prediction_group, on='id_lead_tbl', how='right')

    max_date = df_complete_date_prediction['last_modified_date_opp_tbl'].max()
    df_complete_date_prediction['remaining_days_prediction'] = df_complete_date_prediction[
        'remaining_days_prediction'].astype(int)

    df_complete_date_prediction['predicted_date'] = np.where(
        (df_complete_date_prediction['last_stage_date'] + pd.to_timedelta(
            df_complete_date_prediction['remaining_days_prediction'], unit='D')) > max_date,
        df_complete_date_prediction['last_stage_date'] + pd.to_timedelta(
            df_complete_date_prediction['remaining_days_prediction'], unit='D'),
        max_date + pd.to_timedelta(df_complete_date_prediction['remaining_days_prediction'], unit='D')
    )

    return df_complete_date_prediction


def replace_previous_dates(date):
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if date < current_month_start:
        return current_month_start
    else:
        return date


def apply_date_replacement(df_complete_date_prediction: pd.DataFrame) -> pd.DataFrame:
    # Apply the function to the 'predicted_date' column
    df_complete_date_prediction['predicted_date'] = df_complete_date_prediction['predicted_date'].apply(
        replace_previous_dates)
    # display(df_complete_date_prediction)

    return df_complete_date_prediction


def write_df_to_dbfs(df_complete_date_prediction: pd.DataFrame):
    file_name_with_prefix = "Final_Predicted_dates_" + file_name
    df_complete_date_prediction.to_csv(f"{path}/{file_name_with_prefix}", index=False, mode='w')
    print(f"\ndf_complete_date_prediction written to : {path}/{file_name_with_prefix}\n")


def model_steps():
    df = retrieve_source_df()
    df = cast_datetime_columns(df)
    df = clean_data(df)
    df = handle_outliers(df)
    df, df_base = run_last_stage_date_calculations(df)
    df, df_base = apply_end_date(df)
    df = transpose_pd_df(df)
    df = apply_stage_mapping(df)
    df_train, df_prod = retrieve_training_pd_dfs(df)
    df_prediction_group = train_model(df_train, df_prod)
    df_complete_date_prediction = apply_predicted_date(df_base, df_prediction_group)
    df_complete_date_prediction = apply_date_replacement(df_complete_date_prediction)
    write_df_to_dbfs(df_complete_date_prediction)


@log_general_info(
    env=locals(),
    etl_data="data_science__lead_prediction__predicting_days_model",
    script_path=script_path,
    data_sources_type="lakehouse"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    print(f"Spark UI Url: {spark_ui_url}")

    data_source_n_status = []

    logger_helper = LoggerHelper(source=source_files)
    try:
        model_steps()
        logger_helper.log_status()

    except Exception as e:
        msg = f"Error running predicting_days_model:\n{traceback.format_exc()}"
        logger_helper.log_status(traceback=msg, failed=True)

    data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())
