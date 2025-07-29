from great_expectations.data_context import BaseDataContext
from great_expectations.data_context.types.base import DataContextConfig, FilesystemStoreBackendDefaults

import great_expectations as ge
from great_expectations.data_context.data_context import DataContext
import os

context = None


def get_or_initialise_data_context() -> DataContext:
    """
    This data context can be used for your local development
    :return: BaseDataContext built from configurations in great_expectations.yml file
    """
    global context
    if context is None:
        if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
            context = DataContext(context_root_dir="/dbfs/great_expectations")  # for databricks run
        else:
            context = ge.get_context()  # for local run
        return context
    return context


# def get_or_initialise_data_context_databricks():
#     """
#     This is the dbfs data context we will use in databricks as we probably will not be using the yml configuration
#     file like we would for local development.
#     :return: BaseDataContext with in-memory project configuration
#     """
#     dir_prefix = "/Users/muhammad-saeedfalowo/Documents/codebase/lakehouse/dbx_demo_job/scripts/ms_asset"
#     root_directory = dir_prefix+"/dbfs/great_expectations/"
#     data_context_config = DataContextConfig(
#         store_backend_defaults=FilesystemStoreBackendDefaults(root_directory=root_directory)
#     )
#     return BaseDataContext(project_config=data_context_config)


def open_data_docs() -> None:
    get_or_initialise_data_context().open_data_docs()
