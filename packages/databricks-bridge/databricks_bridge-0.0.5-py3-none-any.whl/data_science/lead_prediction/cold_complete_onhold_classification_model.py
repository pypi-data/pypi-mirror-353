# Databricks notebook source
from typing import Tuple
import os
import traceback
import pandas as pd
import numpy as np
from datetime import datetime

from pyspark.sql import SparkSession

# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from keras.models import Sequential
# from keras.layers import LSTM, Dense
# from keras.utils import to_categorical
# from keras.layers import Dropout
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.utils import to_categorical

from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

from data_science.lead_prediction.df_utils.cold_complete_onhold_model import column_names_definition as col_def

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/cold_complete_onhold_classification_model.py"

today_date = datetime.today().strftime('%B_%m%d%Y')
# Create the file name
file_name = f"{today_date}.csv"
# file_name='May_05022024.csv'
print(file_name)
path = "/dbfs/FileStore/Lead_Pred_test"
source_files = []


def retrieve_source_df() -> pd.DataFrame:
    file_path = f"{path}/{file_name}"
    source_files.append(file_path)
    print(f"\nretrieving file from: {file_path}\n")
    df1 = pd.read_csv(file_path)
    return df1


def format_pd_df_column(df1: pd.DataFrame):
    df_pandas=df1.copy()

    column_name = 'formatted_est_billable_assets_opp_tbl'

    df_pandas[column_name] = df_pandas[column_name].astype(str)

    # Remove non-numeric characters using regular expressions
    df_pandas[column_name] = df_pandas[column_name].replace("[^0-9.]", "", regex=True)

    # Replace empty strings with NaN
    df_pandas[column_name] = df_pandas[column_name].replace('', np.nan)

    # Convert to float
    df_pandas[column_name] = df_pandas[column_name].astype(float)

    # Fill NaN values with 0.00
    df_pandas[column_name] = df_pandas[column_name].fillna(0.00)

    return df_pandas


def pd_df_fillna(df_pandas: pd.DataFrame) -> pd.DataFrame:
    df_pandas['current_stage_lead_tbl'] = df_pandas.apply(lambda row: 'Converted' if pd.isnull(row['current_stage_lead_tbl']) and not pd.isnull(row['id_opp_tbl']) else row['current_stage_lead_tbl'], axis=1)
    df_pandas['current_stage_opp_tbl'] = df_pandas.apply(lambda row: row['current_stage_lead_tbl'] if pd.notna(row['current_stage_lead_tbl']) and pd.isna(row['current_stage_opp_tbl']) else row['current_stage_opp_tbl'], axis=1)
    # df_pandas['id_lead_tbl'] = df_pandas.apply(lambda row: row['id_opp_tbl'] if pd.notna(row['id_opp_tbl']) and pd.isna(row['id_lead_tbl']) else row['id_lead_tbl'], axis=1)
    # df_pandas.drop(columns=['id_opp_tbl'],inplace=True)
    mask = df_pandas['account_source_account_tbl'].isnull()
    df_pandas.loc[mask, 'account_source_account_tbl'] = df_pandas.loc[mask, 'lead_source_opp_tbl']

    df_pandas['stage_unqualified_date'] = df_pandas['stage_unqualified_date'].fillna(df_pandas['stage_qualified_date']).fillna(df_pandas['stage_pitch_meeting_set_date']).fillna(df_pandas['stage_converted_date']).fillna(df_pandas['stage_initial_interaction_date']).fillna(df_pandas['stage_initial_analysis_date']).fillna(df_pandas['stage_qa_meeting_date']).fillna(df_pandas['stage_statement_gathering_date']).fillna(df_pandas['stage_hcls_prep_date']).fillna(df_pandas['stage_health_check_meeting_date']).fillna(df_pandas['stage_closing_date']).fillna(df_pandas['stage_on_boarding_date']).fillna(df_pandas['stage_complete_date'])

    df_pandas['stage_qualified_date'] = df_pandas['stage_qualified_date'].fillna(df_pandas['stage_pitch_meeting_set_date']).fillna(df_pandas['stage_converted_date']).fillna(df_pandas['stage_initial_interaction_date']).fillna(df_pandas['stage_initial_analysis_date']).fillna(df_pandas['stage_qa_meeting_date']).fillna(df_pandas['stage_statement_gathering_date']).fillna(df_pandas['stage_hcls_prep_date']).fillna(df_pandas['stage_health_check_meeting_date']).fillna(df_pandas['stage_closing_date']).fillna(df_pandas['stage_on_boarding_date']).fillna(df_pandas['stage_complete_date'])

    df_pandas['stage_pitch_meeting_set_date'] = df_pandas['stage_pitch_meeting_set_date'].fillna(df_pandas['stage_converted_date']).fillna(df_pandas['stage_initial_interaction_date']).fillna(df_pandas['stage_initial_analysis_date']).fillna(df_pandas['stage_qa_meeting_date']).fillna(df_pandas['stage_statement_gathering_date']).fillna(df_pandas['stage_hcls_prep_date']).fillna(df_pandas['stage_health_check_meeting_date']).fillna(df_pandas['stage_closing_date']).fillna(df_pandas['stage_on_boarding_date']).fillna(df_pandas['stage_complete_date'])

    df_pandas['stage_converted_date'] = df_pandas['stage_converted_date'].fillna(df_pandas['stage_initial_interaction_date']).fillna(df_pandas['stage_initial_analysis_date']).fillna(df_pandas['stage_qa_meeting_date']).fillna(df_pandas['stage_statement_gathering_date']).fillna(df_pandas['stage_hcls_prep_date']).fillna(df_pandas['stage_health_check_meeting_date']).fillna(df_pandas['stage_closing_date']).fillna(df_pandas['stage_on_boarding_date']).fillna(df_pandas['stage_complete_date'])

    return df_pandas


def apply_stage_mapping(df_pandas: pd.DataFrame) -> pd.DataFrame:
    df=df_pandas.copy()

    # Define mappings
    stage_mapping = {
        'Shareholder introduction': 0, 'Other': 1, 'Client introduction (after Y1)': 2,
        'Search (paid/organic)': 3, 'Event (live & virtual)': 4, 'Corporate': 5, 'None': 6,
        'Lead introduction': 7, 'New client introduction': 8, 'Digital advertising': 9,
        'Social lead gen (paid/organic)': 10
    }

    stage_mapping1 = {
        'Shareholder introduction': 0, 'Other': 1, 'Client introduction (after Y1)': 2,
        'Search (paid/organic)': 3, 'Event (live & virtual)': 4, 'Corporate': 5, 'None': 6,
        'Lead introduction': 7, 'New client introduction': 8, 'Digital advertising': 9,
        'Social lead gen (paid/organic)': 10
    }

    stage_mapping3 = {'0.25': 0, '0.35': 1, 'July 2022': 2, 'October 2023': 3}

    stage_mapping4 = {'0.25': 0, '0.35': 1, 'July 2022': 2, 'October 2023': 3}

    stage_mapping5 = {
        'Quarterly': 0, 'Monthly': 1, None: 2
    }

    stage_mapping6 = {'Professional': 0, 'Retail': 1}

    stage_mapping7 = {'Male': 0, 'Female': 1}

    stage_mapping8 = {'Mr.': 0, 'Mrs.': 1, 'Ms.': 2, 'Dr.': 3, 'Sir': 4}

    stage_mapping9={'Closed':0 ,'Omitted':1 ,'Pipeline':2}

    stage_mapping10={'Approved':0 ,'Missing':1 ,'In Progress':2}

    stage_mapping11={'Standard':0, 'High':1}
    stage_mapping12={'Group Client':0, 'In Progress':1, 'Inactive':2, 'Offboarding':3, 'Client':4}
    stage_mapping13={'No':0, 'Yes':1}
    stage_mapping14={'United Kingdom':0, 'Switzerland':1, 'Israel':2, 'Monaco':3, 'Hong Kong':4,
     'Guernsey':5,'Italy':6, 'Kenya':8, 'Malaysia':9, 'Belgium':10, 'United Arab Emirates':11}

    # Apply mappings to create new columns
    df['lead_source_opp_tbl_encoded'] = df['lead_source_opp_tbl'].map(stage_mapping).replace(np.nan, -1).astype(int)
    df['account_source_account_tbl_encoded'] = df['account_source_account_tbl'].map(stage_mapping1).replace(np.nan, -1).astype(int)
    df['fee_account_tbl_encoded'] = df['fee_account_tbl'].map(stage_mapping3).replace(np.nan, -1).astype(int)
    df['invoicing_period_account_tbl_encoded'] = df['invoicing_period_account_tbl'].map(stage_mapping4).replace(np.nan, -1).astype(int)
    df['occupation_account_tbl_encoded'] = df['occupation_account_tbl'].map(stage_mapping5).replace(np.nan, -1).astype(int)
    df['client_classification_account_tbl_encoded'] = df['client_classification_account_tbl'].map(stage_mapping6).replace(np.nan, -1).astype(int)
    df['gender_account_tbl_encoded'] = df['gender_account_tbl'].map(stage_mapping7).replace(np.nan, -1).astype(int)
    df['salutation_account_tbl_encoded'] = df['salutation_account_tbl'].map(stage_mapping8).replace(np.nan, -1).astype(int)
    df['forecast_category_name_opp_tbl_encoded']=df['forecast_category_name_opp_tbl'].map(stage_mapping9).replace(np.nan, -1).astype(int)
    df['kyc_status__c_account_tbl_encoded']=df['kyc_status__c_account_tbl'].map(stage_mapping10).replace(np.nan, -1).astype(int)
    df['risk_level_account_tbl_encoded']=df['risk_level_account_tbl'].map(stage_mapping11).replace(np.nan, -1).astype(int)
    df['stage_account_tbl_encoded']=df['stage_account_tbl'].map(stage_mapping12).replace(np.nan, -1).astype(int)
    df['us_connected_person_account_tbl_encoded']=df['us_connected_person_account_tbl'].map(stage_mapping13).replace(np.nan, -1).astype(int)
    df['primary_residency_account_tbl_encoded']=df['primary_residency_account_tbl'].map(stage_mapping14).replace(np.nan, -1).astype(int)

    return df


def cast_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    # List of columns to convert to datetime
    date_columns = col_def.date_columns

    # Convert columns to datetime
    for column in date_columns:
        df[column] = pd.to_datetime(df[column])

    # # Fill missing values in 'stage_on_hold_date_opp_tbl' column with specified date
    # df['stage_on_hold_date_opp_tbl'].fillna(pd.to_datetime('1800-01-01 00:00:00+00:00'), inplace=True)

    return df


def run_last_stage_days_calculations(df: pd.DataFrame) -> pd.DataFrame:
    null_date = pd.to_datetime('1800-01-01 00:00:00+00:00')
    max_date = df['last_modified_date_opp_tbl'].max()

    def assign_last_stage(row):
        if (row['stage_on_boarding_date'] != null_date) & (row['stage_complete_date'] != null_date):
            days = (row['stage_complete_date'] - row['stage_on_boarding_date']).days if row['stage_cold_date_opp_tbl'] == null_date else (row['stage_cold_date_opp_tbl'] - row['stage_on_boarding_date']).days
            return pd.Series({'last_stage_number': 12, 'last_stage_days': days})
        elif row['stage_on_boarding_date'] != null_date:
            days = (max_date - row['stage_on_boarding_date']).days if row['stage_cold_date_opp_tbl'] == null_date else (row['stage_cold_date_opp_tbl'] - row['stage_on_boarding_date']).days
            return pd.Series({'last_stage_number': 11, 'last_stage_days': days})
        elif row['stage_closing_date'] != null_date:
            days = (max_date - row['stage_closing_date']).days if row['stage_cold_date_opp_tbl'] == null_date else (row['stage_cold_date_opp_tbl'] - row['stage_closing_date']).days
            return pd.Series({'last_stage_number': 10, 'last_stage_days': days})
        elif row['stage_health_check_meeting_date'] != null_date:
            days = (max_date - row['stage_health_check_meeting_date']).days if row['stage_cold_date_opp_tbl'] == null_date else (row['stage_cold_date_opp_tbl'] - row['stage_health_check_meeting_date']).days
            return pd.Series({'last_stage_number': 9, 'last_stage_days': days})
        elif row['stage_hcls_prep_date'] != null_date:
            days = (max_date - row['stage_hcls_prep_date']).days if row['stage_cold_date_opp_tbl'] == null_date else (row['stage_cold_date_opp_tbl'] - row['stage_hcls_prep_date']).days
            return pd.Series({'last_stage_number': 8, 'last_stage_days': days})
        elif row['stage_statement_gathering_date'] != null_date:
            days = (max_date - row['stage_statement_gathering_date']).days if row['stage_cold_date_opp_tbl'] == null_date else (row['stage_cold_date_opp_tbl'] - row['stage_statement_gathering_date']).days
            return pd.Series({'last_stage_number': 7, 'last_stage_days': days})
        elif row['stage_qa_meeting_date'] != null_date:
            days = (max_date - row['stage_qa_meeting_date']).days if row['stage_cold_date_opp_tbl'] == null_date else (row['stage_cold_date_opp_tbl'] - row['stage_qa_meeting_date']).days
            return pd.Series({'last_stage_number': 6, 'last_stage_days': days})
        elif row['stage_initial_analysis_date'] != null_date:
            days = (max_date - row['stage_initial_analysis_date']).days if row['stage_cold_date_opp_tbl'] == null_date else (row['stage_cold_date_opp_tbl'] - row['stage_initial_analysis_date']).days
            return pd.Series({'last_stage_number': 5, 'last_stage_days': days})
        # elif row['stage_converted_date'] != null_date:
        #     days = (max_date - row['stage_converted_date']).days if row['stage_cold_date_opp_tbl'] == null_date else (row['stage_cold_date_opp_tbl'] - row['stage_converted_date']).days
        #     return pd.Series({'last_stage_number': 4, 'last_stage_days': days})
        elif row['stage_pitch_meeting_set_date'] != null_date:
            days = (max_date - row['stage_pitch_meeting_set_date']).days if row['stage_cold_date_opp_tbl'] == null_date else (row['stage_cold_date_opp_tbl'] - row['stage_pitch_meeting_set_date']).days
            return pd.Series({'last_stage_number': 3, 'last_stage_days': days})
        elif row['stage_qualified_date'] != null_date:
            days = (max_date - row['stage_qualified_date']).days if row['stage_cold_date_opp_tbl'] == null_date else (row['stage_cold_date_opp_tbl'] - row['stage_qualified_date']).days
            return pd.Series({'last_stage_number': 2, 'last_stage_days': days})
        elif row['stage_unqualified_date'] != null_date:
            days = (max_date - row['stage_unqualified_date']).days if row['stage_cold_date_opp_tbl'] == null_date else (row['stage_cold_date_opp_tbl'] - row['stage_unqualified_date']).days
            return pd.Series({'last_stage_number': 1, 'last_stage_days': days})
        else:
            if row['stage_cold_date_opp_tbl'] != null_date:
                days = (row['stage_cold_date_opp_tbl'] - row['created_date_opp_tbl']).days
            elif row['stage_on_hold_date_opp_tbl'] != null_date:
                days = (row['stage_on_hold_date_opp_tbl'] - row['created_date_opp_tbl']).days
            else:
                days = (max_date - row['created_date_opp_tbl']).days
            return pd.Series({'last_stage_number': 0, 'last_stage_days': days})

    df[['last_stage_number', 'last_stage_days']] = df.apply(assign_last_stage, axis=1)
    df.loc[df['current_stage_opp_tbl_encoded'] == 8, 'last_stage_days'] = 0

    return df


def get_final_pd_df(df: pd.DataFrame):
    cols_req = col_def.cols_req
    final_df=df[cols_req]
    # final_df['last_stage_days'] = final_df['last_stage_days'].replace(-1, 0)
    # final_df['total_and_last_stage_days'] = final_df['total_days'] + final_df['last_stage_days']

    return final_df


def filter_pd_df(final_df: pd.DataFrame) -> pd.DataFrame:
    filtered_df = final_df[
        (final_df['current_stage_opp_tbl_encoded'] == 8) | (final_df['current_stage_opp_tbl_encoded'] == 9) | (
                    final_df['current_stage_opp_tbl_encoded'] == 10)]

    return filtered_df


def pd_df_float_columns_fillna(filtered_df: pd.DataFrame) -> pd.DataFrame:
    # Identify float columns
    float_columns = filtered_df.select_dtypes(include=['float']).columns

    # Fill null values in float columns with -1.0
    filtered_df[float_columns] = filtered_df[float_columns].fillna(-1.0)

    return filtered_df


def cast_bool_to_int(filtered_df: pd.DataFrame) -> pd.DataFrame:
    # Select boolean columns
    boolean_columns = filtered_df.select_dtypes(include=bool).columns

    # Convert boolean columns to integers
    filtered_df[boolean_columns] = filtered_df[boolean_columns].astype(int)

    return filtered_df


def build_and_run_training_model(filtered_df: pd.DataFrame):
    X = filtered_df[['lead_source_opp_tbl_encoded',
                     'subject_to_vat_account_tbl',
                     'account_source_account_tbl_encoded',
                     'date_qualified_has_value_lead_tbl',
                     'date_unqualified_has_value_lead_tbl',
                     'fee_account_tbl_encoded',
                     'is_shareholder_account_tbl',
                     'y__champion_account_tbl',
                     'link_events_to_account_account_tbl',
                     'kyc_approved_count_account_tbl',
                     'invoicing_period_account_tbl_encoded',
                     'occupation_account_tbl_encoded',
                     'clients_opportunities_company_tbl',
                     'client_classification_account_tbl_encoded',
                     'expected_fee_rate_opp_tbl',
                     'gender_account_tbl_encoded',
                     'salutation_account_tbl_encoded',
                     'formatted_est_billable_assets_opp_tbl',
                     'no_of_days_in_stage_unqualified_date',
                     'no_of_days_in_stage_qualified_date',
                     'no_of_days_in_stage_pitch_meeting_set_date',
                     'no_of_days_in_stage_initial_interaction_date',
                     'no_of_days_in_stage_initial_analysis_date',
                     'no_of_days_in_stage_qa_meeting_date',
                     'no_of_days_in_stage_statement_gathering_date',
                     'no_of_days_in_stage_hcls_prep_date',
                     'no_of_days_in_stage_health_check_meeting_date',
                     'no_of_days_in_stage_closing_date',
                     'no_of_days_in_stage_on_boarding_date', 'no_of_days_in_stage_converted_date',
                     'deemed_domicile_account_tbl', 'forecast_category_name_opp_tbl_encoded',
                     'kyc_record_count_account_tbl', 'kyc_status__c_account_tbl_encoded',
                     'person_has_opted_out_of_email_account_tbl', 'probability_opp_tbl',
                     'risk_level_account_tbl_encoded', 'stage_account_tbl_encoded',
                     'us_connected_person_account_tbl_encoded', 'x1_year_experience_account_tbl',
                     'primary_residency_account_tbl_encoded', 'last_stage_days']]
    y = filtered_df['current_stage_opp_tbl_encoded']

    # Perform one-hot encoding on the target variable
    y_encoded = to_categorical(y)

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Define the number of folds for cross-validation
    num_folds = 5  # You can adjust this as needed

    # Initialize cross-validation
    kf = KFold(n_splits=num_folds, shuffle=True, random_state=42)

    # Store accuracies for each fold
    fold_accuracies = []

    # Initialize dictionary to store class-wise accuracies across all folds
    class_accuracies = {}

    # Loop over each fold
    for fold, (train_indices, val_indices) in enumerate(kf.split(X_scaled)):
        fold += 1
        print(f"Fold {fold}/{num_folds}")

        X_train_fold, X_val_fold = X_scaled[train_indices], X_scaled[val_indices]
        y_train_fold, y_val_fold = y_encoded[train_indices], y_encoded[val_indices]

        # Reshape the data for LSTM input
        X_train_fold_reshaped = np.reshape(X_train_fold, (X_train_fold.shape[0], 1, X_train_fold.shape[1]))
        X_val_fold_reshaped = np.reshape(X_val_fold, (X_val_fold.shape[0], 1, X_val_fold.shape[1]))

        # Define the LSTM model (same as before)
        model = Sequential()
        model.add(LSTM(units=50, activation='relu',
                       input_shape=(X_train_fold_reshaped.shape[1], X_train_fold_reshaped.shape[2])))
        model.add(Dropout(0.2))
        model.add(Dense(units=y_encoded.shape[1], activation='softmax'))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

        # Train the model
        model.fit(X_train_fold_reshaped, y_train_fold, epochs=10, batch_size=32,
                  validation_data=(X_val_fold_reshaped, y_val_fold))

        # Make predictions on the validation set
        y_pred_probs = model.predict(X_val_fold_reshaped)
        y_pred = np.argmax(y_pred_probs, axis=1)

        # Convert one-hot encoded y_val_fold back to categorical labels
        y_true = np.argmax(y_val_fold, axis=1)

        # Calculate accuracy for each class
        for class_label in set(y_true):
            indices = np.where(y_true == class_label)[0]
            class_accuracy = np.mean(y_pred[indices] == class_label)

            # Update class_accuracies dictionary
            if class_label in class_accuracies:
                class_accuracies[class_label].append(class_accuracy)
            else:
                class_accuracies[class_label] = [class_accuracy]

    # Calculate mean class-wise accuracies across all folds
    mean_class_accuracies = {class_label: np.mean(accuracies) for class_label, accuracies in class_accuracies.items()}

    # Print class-wise accuracy
    for class_label, accuracy in mean_class_accuracies.items():
        print(f"Class {class_label}: Mean Accuracy = {accuracy}")

    return model


def retrieve_in_progress_leads(final_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # in_progress_leads = final_df[~((final_df['current_stage_opp_tbl_encoded'] == 8) |
    #                           (final_df['current_stage_opp_tbl_encoded'] == 9) |
    #                           (final_df['current_stage_opp_tbl_encoded'] == 10) |
    #                           (final_df['current_stage_opp_tbl_encoded'] == 11))]
    in_progress_leads = final_df[~((final_df['current_stage_opp_tbl_encoded'] == 8) |
                              (final_df['current_stage_opp_tbl_encoded'] == 9) |
                              (final_df['current_stage_opp_tbl_encoded'] == 10))]

    # Identify float columns
    float_columns = in_progress_leads.select_dtypes(include=['float']).columns

    # Fill null values in float columns with -1.0
    in_progress_leads[float_columns] = in_progress_leads[float_columns].fillna(-1.0)

    df_in_progress_leads = in_progress_leads.drop(['id_lead_tbl', 'current_stage_opp_tbl_encoded'], axis=1)

    boolean_columns = df_in_progress_leads.select_dtypes(include=bool).columns
    df_in_progress_leads[boolean_columns] = df_in_progress_leads[boolean_columns].astype(int)

    return in_progress_leads, df_in_progress_leads


def retrieve_predictions(df_in_progress_leads, model):
    scaler = StandardScaler()
    X_new_scaled = scaler.fit_transform(df_in_progress_leads)

    # Reshape the data for LSTM input (samples, time steps, features)
    X_new_scaled1 = np.reshape(X_new_scaled, (X_new_scaled.shape[0], 1, X_new_scaled.shape[1]))

    # Make predictions
    predictions = model.predict(X_new_scaled1)

    return predictions


def retrieve_result_pd_df(predictions, in_progress_leads) -> pd.DataFrame:
    # Perform inverse transformation on predictions
    predicted_classes = np.argmax(predictions, axis=1)

    # Create a DataFrame with predictions
    predictions_df = pd.DataFrame(predicted_classes, columns=['predicted_stage'])

    # Concatenate the predictions DataFrame with the original DataFrame
    result_df = pd.concat([in_progress_leads.reset_index(drop=True), predictions_df], axis=1)

    return result_df


def write_df_to_dbfs(result_df: pd.DataFrame):
    # display(result_df)
    result = result_df[['id_lead_tbl', 'predicted_stage']]
    file_name_with_prefix = "LSTM_predictions_" + file_name
    result.to_csv(f"{path}/{file_name_with_prefix}", index=False, mode='w')
    print(f"\nresult_df written to : {path}/{file_name_with_prefix}\n")


def model_steps():
    df = retrieve_source_df()
    df = format_pd_df_column(df)
    df = pd_df_fillna(df)
    df = apply_stage_mapping(df)
    df = cast_datetime_columns(df)
    df = run_last_stage_days_calculations(df)
    final_df = get_final_pd_df(df)
    filtered_df = filter_pd_df(final_df)
    filtered_df = pd_df_float_columns_fillna(filtered_df)
    filtered_df = cast_bool_to_int(filtered_df)
    model = build_and_run_training_model(filtered_df)
    in_progress_leads, df_in_progress_leads = retrieve_in_progress_leads(final_df)
    predictions = retrieve_predictions(df_in_progress_leads, model)
    result_df = retrieve_result_pd_df(predictions, in_progress_leads)
    write_df_to_dbfs(result_df)


@log_general_info(
    env=locals(),
    etl_data="data_science__lead_prediction__cold_complete_onhold_classification_model",
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
        msg = f"Error running cold_complete_onhold_classification_model:\n{traceback.format_exc()}"
        logger_helper.log_status(traceback=msg, failed=True)

    data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_etl(locals())
