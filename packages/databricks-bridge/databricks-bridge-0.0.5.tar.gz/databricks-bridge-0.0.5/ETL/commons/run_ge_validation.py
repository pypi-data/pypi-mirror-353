from pyspark.sql.dataframe import DataFrame
from ETL.ge_utils.ge_data_runner import GreatExpectationsDataRunner
import time


def build_ge_arguments_and_run_validation(data_source: str, table_file_tag: str, df: DataFrame):
    # build ge arguments
    ge_args = {
        "execution_engine": "SparkDFExecutionEngine",
        "data_asset_name": f"{data_source}_{table_file_tag}_asset",
        "data_source_name": f"{data_source}_{table_file_tag}_data_source",
        "data_connector_name": f"{data_source}_{table_file_tag}_connector",
        "expectation_suite_name": f"{data_source}_{table_file_tag}_expectation_suite",
        "checkpoint_name": f"{data_source}_{table_file_tag}_checkpoint",
    }
    # run great expectation validation
    run_ge_validation(df, ge_args)


def run_ge_validation(df: DataFrame, ge_args: dict):
    print("Running GE Validation...")
    start_time = time.time()
    ge_runner = GreatExpectationsDataRunner(
        execution_engine=ge_args["execution_engine"],
        data_asset_name=ge_args["data_asset_name"],
        data_source_name=ge_args["data_source_name"],
        data_connector_name=ge_args["data_connector_name"],
        expectation_suite_name=ge_args["expectation_suite_name"],
        checkpoint_name=ge_args["checkpoint_name"],
    )
    ge_runner.setup_validations_initial(df)

    results = ge_runner.run_validations(df)

    print(results)
    print("Finished GE Validation...")
    print(f"Duration: {time.time() - start_time} seconds\n")