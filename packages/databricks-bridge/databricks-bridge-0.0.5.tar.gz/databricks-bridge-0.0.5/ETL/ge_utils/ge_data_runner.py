from datetime import datetime
from typing import Dict, Optional, Union

import pandas as pd
import pyspark
from ruamel import yaml

from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.exceptions import CheckpointNotFoundError
from great_expectations.profile.user_configurable_profiler import UserConfigurableProfiler
from great_expectations.validator.validator import Validator

from ETL.ge_utils.commons import *
from ETL.ge_utils.constants import *
from ETL.ge_utils.exceptions import *
from ETL.ge_utils.loggers import logger


class GreatExpectationsDataRunner:

    def __init__(
            self,
            execution_engine: engine,
            data_asset_name: str,
            data_source_name: str,
            data_connector_name: str,
            expectation_suite_name: str,
            checkpoint_name: str,
            batch_identifiers: Optional[Dict[str, str]] = None
    ):
        self.context = get_or_initialise_data_context()
        if execution_engine not in ("PandasExecutionEngine", "SparkDFExecutionEngine"):
            raise IncorrectExecutionEngine("Execution engine must be PandasExecutionEngine or SparkDFExecutionEngine")
        self.execution_engine = execution_engine
        self.batch_identifiers = batch_identifiers if batch_identifiers is not None else {}
        self.data_asset_name = data_asset_name
        self.data_source_name = data_source_name
        self.data_connector_name = data_connector_name
        self.expectation_suite_name = expectation_suite_name
        self.checkpoint_name = checkpoint_name

    def __repr__(self):
        return f"Data Validator class for pipeline ETL for data asset: {self.data_asset_name}"

    def setup_validations_initial(self, df: Union[pd.DataFrame, pyspark.sql.DataFrame]):
        try:
            logger.info("Seeing if you have already created a great expectations flow for this pipeline...")
            self.context.get_checkpoint(self.checkpoint_name)
            logger.info("Great Expectations setup already completed once before...skipping...")
        except CheckpointNotFoundError:
            logger.info("Great Expectations checkpoint not found therefore creating all steps...")
            self._create_data_source()
            self._create_profiled_expectation_suite(df)
            self._create_checkpoint()
            logger.info("Great Expectations initial set-up complete")
        except Exception as e:
            raise Exception(f"Error in executing the initial run: {e}")

    def run_validations(self, df: Union[pd.DataFrame, pyspark.sql.DataFrame]) -> Dict:
        try:
            return self._run_checkpoint(df)
        except CheckpointNotFoundError as e:
            raise CheckpointNotFoundError(e)
        except Exception as e:
            raise Exception(f"Something has gone wrong running the validations: {e}")

    def _create_data_source(self):
        if self.data_source_name not in [x['name'] for x in self.context.list_datasources()]:
            config = {
                "name": self.data_source_name,
                "class_name": "Datasource",
                "module_name": "great_expectations.datasource",
                "execution_engine": {
                    "module_name": "great_expectations.execution_engine",
                    "class_name": self.execution_engine,
                },
                "data_connectors": {
                    self.data_connector_name: {
                        "class_name": "RuntimeDataConnector",
                        "batch_identifiers": ["timestamp", *self.batch_identifiers.keys()],
                    },
                },
            }

            if self.execution_engine == "SparkDFExecutionEngine":
                config["execution_engine"] = {
                    "module_name": "great_expectations.execution_engine",
                    "class_name": self.execution_engine,
                    "force_reuse_spark_context": "true"
                }

            try:
                self.context.test_yaml_config(yaml.dump(config))
                self.context.add_datasource(**config)
            except Exception as e:
                raise CreateDataSourceError(f"Error in creating the data source: {e}")

    def _create_profiled_expectation_suite(self, df: Union[pd.DataFrame, pyspark.sql.DataFrame]):
        """
        This will create an expectation suite and then the profiler will over-fit your data to auto-generate
        expectations.
        """
        try:
            self.context.create_expectation_suite(expectation_suite_name=self.expectation_suite_name)
            validator = self._get_validator(df)
            profiler = UserConfigurableProfiler(profile_dataset=validator)
        except Exception as e:
            raise CreateExpectationSuiteError(f"Something horrible has happened during creating suite process: {e}")

        try:
            profiler.build_suite()
        except Exception as e:
            logger.error(f"Build suite error, one of the expectations caused an error: {e}")
            logger.info("Continuing expectation suite creation...")
        finally:
            validator.save_expectation_suite()

    def _create_runtime_batch_request(self, df: Union[pd.DataFrame, pyspark.sql.DataFrame]) -> RuntimeBatchRequest:
        return RuntimeBatchRequest(
            datasource_name=self.data_source_name,
            data_connector_name=self.data_connector_name,
            data_asset_name=self.data_asset_name,
            runtime_parameters={"batch_data": df},
            batch_identifiers={
                "timestamp": str(datetime.now()),
                **self.batch_identifiers
            }
        )

    def _create_checkpoint(self):
        config = {
            "name": self.checkpoint_name,
            "config_version": 1,
            "class_name": "SimpleCheckpoint",
            "expectation_suite_name": self.expectation_suite_name
        }
        self.context.add_checkpoint(**config)

    def _get_validator(self, df: Union[pd.DataFrame, pyspark.sql.DataFrame]) -> Validator:
        return self.context.get_validator(
            batch_request=self._create_runtime_batch_request(df),
            expectation_suite_name=self.expectation_suite_name
        )

    def _run_checkpoint(self, df: Union[pd.DataFrame, pyspark.sql.DataFrame]) -> Dict:
        results = self.context.run_checkpoint(
            checkpoint_name=self.checkpoint_name,
            run_name=f"{self.data_asset_name}-{str(datetime.now())}",
            validations=[
                {"batch_request": self._create_runtime_batch_request(df)}
            ]
        )
        return results.to_json_dict()
