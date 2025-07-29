# Databricks notebook source
import os
import traceback
from typing import Tuple

import numpy as np

import pandas as pd
from pandas.tseries.offsets import MonthEnd

from pyspark.sql import SparkSession

from ETL.scripts.asset.df_utils.morningstar_IFLS_df_utils import db_name

from ETL.commons.ease_of_use_fcns import LoggerHelper
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info

set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/ifls_performance_calculations.py"
full_table_name = "performance_calculations"
summary_table_name = "performance_calculations_summary"

# Inputs & solutions basics
solution_value = 100000
start_date = pd.Timestamp("2018-12-31")
# end_date = pd.Timestamp('2023-10-17')  # NOTE: can be changed so it takes yesterday's date
end_date = pd.Timestamp.today() - pd.Timedelta(days=2)
rebalancing = True  # True values will activate end of month rebalancing
file_path = '/dbfs/FileStore/IFLS/Factsheet_Generator_v1_1.xlsx'


def request_morningstar_data(spark: SparkSession):
    query = "SELECT ASSET_ISIN, DATE, VALUE, B.NAME, C.ISO_CODE AS ASSET_BASE_CURRENCY FROM ASSETS.TOTAL_RETURN_INDEX	A INNER JOIN ASSETS.ASSET	B		 ON A.ASSET_ISIN = B.ISIN INNER JOIN CONSTANTS_V2.CURRENCY	C ON B.BASE_CURRENCY = C.ID WHERE ASSET_ISIN IN (select DISTINCT ISIN	FROM INVESTMENT_SOLUTION.FUND) order by 1 DESC,2;"
    df = spark.sql(query).toPandas()
    new_column_names = {
        'ASSET_ISIN': 'Asset ISIN',
        'DATE': 'Date',
        'VALUE': 'TRI',
        'NAME': 'Asset Name',
        'ASSET_BASE_CURRENCY': 'Asset Base Currency'
    }
    df = df.rename(columns=new_column_names)
    df['Date'] = pd.to_datetime(df['Date'])

    # Reshape the 'morningstar_data' DataFrame using pivot
    df = df.pivot(index='Date', columns='Asset ISIN', values='TRI')
    df.reset_index(inplace=True)
    df.iloc[:, 1:] = df.iloc[:, 1:].astype('float64')
    return df


def request_fx_data(spark: SparkSession, start_date, end_date):
    query = "SELECT * FROM currency.rate_usd WHERE currency IN ('GBP', 'EUR', 'JPY', 'CHF') AND date BETWEEN '2018-12-31' AND '2024-12-31';"
    df = spark.sql(query).toPandas()
    df['Date'] = pd.to_datetime(df['date'])

    # Reshape the fx data DataFrame using pivot
    df = df.pivot(index='Date', columns='currency', values='price')
    df.reset_index(inplace=True)

    # Rename columns to indicate the USD currency pair and calculate remaining pais
    df.columns = ['USD/' + col if col != 'Date' else col for col in df.columns]

    df['EUR/GBP'] = df['USD/GBP'] * (1 / df['USD/EUR'])
    df['CHF/GBP'] = df['USD/GBP'] * (1 / df['USD/CHF'])
    df['JPY/GBP'] = df['USD/GBP'] * (1 / df['USD/JPY'])
    df['GBP/EUR'] = 1 / df['EUR/GBP']
    df['EUR/USD'] = 1 / df['USD/EUR']

    # Create the dataframe that will hold the cleaned FX data
    df_fx_returns = pd.DataFrame({'Date': pd.date_range(start=start_date, end=end_date, freq='D')})

    # Set the 'Date' column as the index for both DataFrames
    df.set_index('Date', inplace=True)
    df_fx_returns.set_index('Date', inplace=True)

    # Reindex 'df' to match the dates in 'df_fx_returns' and forward-fill missing values
    df = df.reindex(df_fx_returns.index).ffill().reset_index()
    df_fx_returns = df.copy()

    # Calculate currency pair returns
    df_fx_returns.iloc[:, 1:] = df_fx_returns.iloc[:, 1:].astype('float64').pct_change()
    return df_fx_returns


def extract_excel_sheets():
    inv_solutions_sheet_name = 'Inv Solutions'

    # Create the investment_solutions dataframe
    df_investment_solutions = pd.read_excel(file_path, sheet_name=inv_solutions_sheet_name, header=0)
    df_investment_solutions = pd.DataFrame(df_investment_solutions)
    return df_investment_solutions


def extract_solution_basics(df_investment_solutions, solution_id):
    # Extract the number of assets to iterate through for each investment solution
    num_assets = df_investment_solutions[df_investment_solutions['Solution ID'] == solution_id]['Asset ISIN'].nunique()

    # Extract the ISIN codes for each individual asset
    asset_isins = df_investment_solutions[df_investment_solutions['Solution ID'] == solution_id]['Asset ISIN'].unique()
    return num_assets, asset_isins


def find_tri(df_morningstar_pivot, asset_isins, solution_id, start_date, end_date):
    # Create the performance_calculations dataframe
    df_performance_calculations = pd.DataFrame({'Date': pd.date_range(start=start_date, end=end_date, freq='D')})
    df_performance_calculations['Solution ID'] = solution_id
    # Rename the columns to match the desired column names
    for i, asset_ISIN in enumerate(asset_isins, 0):
        column_name_ISIN = f'Asset {i + 1} ISIN'
        column_name_TRI = f'Asset {i + 1} TRI'

        if asset_ISIN not in df_morningstar_pivot.columns:
            print(f"Performance data for asset ISIN {asset_ISIN} in solution ID {solution_id} was not found in Morningstar.")
            return None  # Skip this solution

        # Find matching dates and asset ISINs in 'morningstar_pivot' DataFrame
        matching_values = df_morningstar_pivot.loc[
            df_morningstar_pivot['Date'].isin(df_performance_calculations['Date']), asset_ISIN]

        # Assign the matching values to the 'funds_TRI' DataFrame
        df_performance_calculations[column_name_ISIN] = asset_ISIN
        df_performance_calculations[column_name_TRI] = matching_values.values

    df_performance_calculations = df_performance_calculations.dropna(how='any')  # Remove rows with 'None' values
    df_performance_calculations = df_performance_calculations.reset_index(drop=True)  # Reset the index
    return df_performance_calculations


def calculate_local_return(df_performance_calculations, num_assets):
    for i in range(num_assets):
        # Ensure the 'Asset {i + 1} TRI' column is float64 before pct_change
        df_performance_calculations[f'Asset {i + 1} TRI'] = df_performance_calculations[
            f'Asset {i + 1} TRI'].astype('float64', copy=False)

        df_performance_calculations[f'Asset {i + 1} local return'] = df_performance_calculations[
            f'Asset {i + 1} TRI'].pct_change()
    return df_performance_calculations


def calculate_currency_return(df_performance_calculations, df_fx_returns, num_assets, df_investment_solutions, solution_id):
    for i in range(num_assets):
        # Get the corresponding 'Asset Currency' and 'Solution Base Currency' identifiers
        asset_currency = df_investment_solutions[df_investment_solutions['Solution ID'] == solution_id]['Asset Base Currency'].iloc[i]
        solution_base_currency = \
        df_investment_solutions[df_investment_solutions['Solution ID'] == solution_id]['Solution Base Currency'].iloc[i]

        # Create the column name for the 'Asset i currency return' column
        column_name = f'Asset {i + 1} currency return'

        # Check if the values match and perform the required action
        if asset_currency == solution_base_currency:
            df_performance_calculations[column_name] = 0
        else:
            # Concatenate the currencies
            currency_pair = asset_currency + "/" + solution_base_currency

            # Find the matching column in 'fx_returns' DataFrame based on the currency pair
            currency_return = df_fx_returns.loc[:, currency_pair]

            # Derive the currency return
            df_performance_calculations[column_name] = currency_return * (
                1 + df_performance_calculations[f'Asset {i + 1} local return'])

    return df_performance_calculations


def calculate_total_return(df_performance_calculations, num_assets):
    for i in range(num_assets):
        df_performance_calculations[f'Asset {i + 1} total return'] = df_performance_calculations[
                                                                      f'Asset {i + 1} local return'] + \
                                                                  df_performance_calculations[
                                                                      f'Asset {i + 1} currency return']
    return df_performance_calculations


def calculate_inv_solution_tri(df, num_assets, solution_id, df_investment_solutions):
    df_indv_is = df_investment_solutions[df_investment_solutions['Solution ID'] == solution_id]
    if rebalancing == True:
        # Construct the TRI series for each asset
        for i in range(num_assets):
            target_allocation = df_investment_solutions[df_investment_solutions['Solution ID'] == solution_id]['Weight'].iloc[i]
            df.loc[0, f'Asset {i + 1} value'] = solution_value * target_allocation

        # Create the Total solutions columns
        df['Gross Solution TRI'] = ''
        df.at[0, 'Gross Solution TRI'] = solution_value

        columns = df.filter(like='value').columns

        for row in range(1, len(df)):
            # Check if the current date is at the end of the month
            current_date = df.at[row, 'Date']
            is_end_of_month = (current_date + MonthEnd(0)) == current_date

            if is_end_of_month == True:
                for i in range(num_assets):
                    df.at[row, f'Asset {i + 1} value'] = df.at[
                                                                                   row - 1, f'Asset {i + 1} value'] * (
                                                                                           1 +
                                                                                           df.at[
                                                                                               row, f'Asset {i + 1} total return'])
                df.at[row, 'Gross Solution TRI'] = df.loc[
                    row, [f'Asset {i + 1} value' for i in range(num_assets)]].sum()
                # Rebalance the allocation to target allocation
                if df_indv_is is None or df_indv_is.empty:
                    error_message = f"Solution ID not found. Ensure {solution_id} is a valid Solution ID"
                    print(error_message)
                else:
                    rebalanced_values = df.at[row, 'Gross Solution TRI'] * df_indv_is['Weight'].to_frame().T

                for i in range(num_assets):
                    df.at[row, f'Asset {i + 1} nominal trade'] = rebalanced_values.iloc[0, i] - \
                                                                                       df.at[
                                                                                           row, f'Asset {i + 1} value']
                    df.at[row, f'Asset {i + 1} value'] = rebalanced_values.iloc[0, i]
            else:
                for i in range(num_assets):
                    df.at[row, f'Asset {i + 1} value'] = df.at[
                                                                                   row - 1, f'Asset {i + 1} value'] * (
                                                                                           1 +
                                                                                           df.at[
                                                                                               row, f'Asset {i + 1} total return'])
                df.at[row, 'Gross Solution TRI'] = df.loc[
                    row, [f'Asset {i + 1} value' for i in range(num_assets)]].sum()

    else:
        # Construct the TRI series for each asset
        for i in range(num_assets):
            target_allocation = df_indv_is['Weight'].iloc[i]
            df.loc[0, f'Asset {i + 1} value'] = solution_value * target_allocation
            df.loc[1:, f'Asset {i + 1} value'] = (1 + df[
                f'Asset {i + 1} total return']).cumprod() * df.loc[0, f'Asset {i + 1} value']

        # Add a column 'Gross Solution TRI' that sums all 'Asset i TRI' columns
        columns = df.filter(like='value').columns
        df['Gross Solution TRI'] = df[columns].apply(np.sum, axis=1)

    # Calculate allocation distribution for each 'i' asset
    for i in range(num_assets):
        asset_column = f'Asset {i + 1} value'
        allocation_column = f'Asset {i + 1} allocation'
        df[allocation_column] = df[asset_column] / df[
            'Gross Solution TRI']

    return df


def investment_solution_performance(spark: SparkSession, df_investment_solutions, df_morningstar_data, df_fx_returns, start_date, end_date, solution_id):
    # Define the function that will calculate the TRI for a single investment solution

    # Import the required FX data from Databricks
    df_fx_returns = request_fx_data(spark, start_date, end_date)

    # Import the required investment solution data from an Excel sheet
    df_investment_solutions = extract_excel_sheets()

    # Define the function that will calculate the return series for an individual investment solution
    num_assets, asset_isins = extract_solution_basics(df_investment_solutions, solution_id)

    # Step 1: find the TRI values for the assets
    df_performance_calculations = find_tri(df_morningstar_data, asset_isins, solution_id, start_date, end_date)

    # Skip if no TRI values were found
    if df_performance_calculations is None:
        return None

    # Step 2: calculate the local returns based on TRI
    df_performance_calculations = calculate_local_return(df_performance_calculations, num_assets)

    # Step 3: calculate the currency return for each asset
    df_performance_calculations = calculate_currency_return(df_performance_calculations, df_fx_returns, num_assets,
                                                            df_investment_solutions, solution_id)
    # Step 4: calculate the total return for each asset
    df_performance_calculations = calculate_total_return(df_performance_calculations, num_assets)

    # Step 5: calculate the time series of returns of the investment solution. Monthly rebalancing can be activated
    # (excluding transaction costs)
    df_performance_calculations = calculate_inv_solution_tri(df_performance_calculations, num_assets, solution_id, df_investment_solutions)

    return df_performance_calculations


def all_investment_solutions_performance(spark: SparkSession, df_investment_solutions, df_morningstar_data, df_fx_returns):
    # Define the function that will calculate the TRI for all investment solutions
    # Create an empty DataFrame to store performance calculations and associated Solution IDs
    all_performance_data = pd.DataFrame(columns=['Date', 'Solution ID', 'Gross Solution TRI'])

    for solution_id in df_investment_solutions['Solution ID'].unique():
        df = investment_solution_performance(spark, df_investment_solutions, df_morningstar_data, df_fx_returns, start_date, end_date, solution_id)

        # Skip the solution if df is None (means it was skipped in find_tri)
        if df is None:
            print(f"Skipping solution ID {solution_id} due to missing performance data.")
            continue

        # Append the performance calculations to the all_performance_data DataFrame
        all_performance_data = pd.concat([all_performance_data, df[['Date', 'Solution ID', 'Gross Solution TRI']]])
    all_performance_data = all_performance_data.reset_index(drop=True)
    all_performance_data['Date'] = pd.to_datetime(all_performance_data['Date'])
    return all_performance_data 


def calculate_calendar_year_returns(all_performance_data):
    all_performance_data['Year'] = all_performance_data['Date'].dt.year

    # Group the filtered data by 'Solution ID' and 'Year', selecting the last value of the year
    df_performance_summary = all_performance_data.groupby(['Solution ID', 'Year'])['Gross Solution TRI'].last().reset_index()

    # Calculate annual return
    df_performance_summary['Calendar Year Return'] = (df_performance_summary['Gross Solution TRI'] / df_performance_summary.groupby('Solution ID')['Gross Solution TRI'].shift(1)) - 1
    return df_performance_summary


def write_to_table(spark: SparkSession, pd_df: pd.DataFrame, table_name: str):
    spark_df = spark.createDataFrame(pd_df)
    for col_name in spark_df.columns:
        spark_df = spark_df.withColumnRenamed(col_name, col_name.replace(" ", "_"))

    spark_df.write.format("delta").mode("overwrite").option("mergeSchema", "true").saveAsTable(f"{db_name}.{table_name}")


def execute_calculations(spark: SparkSession):
    # Get data
    df_morningstar_data = request_morningstar_data(spark)
    df_fx_returns = request_fx_data(spark, start_date, end_date)
    df_investment_solutions = extract_excel_sheets()

    # Run analysis for all solutions
    df_master = all_investment_solutions_performance(spark, df_investment_solutions, df_morningstar_data, df_fx_returns)

    # Run calendar year return calculations
    df_performance_summary = calculate_calendar_year_returns(df_master)

    # Write dataframes to tables
    write_to_table(spark, df_master, full_table_name)
    write_to_table(spark, df_performance_summary, summary_table_name)


@log_general_info(
    env=locals(),
    etl_data="ifls_performance_calculations",
    script_path=script_path,
    data_sources_type="lakehouse"
)
def run_etl(env: dict) -> Tuple[SparkSession, list, float]:
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    spark.sql(f"create database if not exists {db_name}")

    data_source_n_status = []
    logger_helper = LoggerHelper(source=file_path)
    try:
        execute_calculations(spark)
        logger_helper.log_status()

    except Exception as e:
        logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

    data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0

# %sql
# SELECT * FROM logging.general_info WHERE etl_data = 'ifls_performance_calculations'


if __name__ == "__main__":
    run_etl(locals())
