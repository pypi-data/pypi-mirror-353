import time
from typing import Tuple, Union, List

from ETL.commons.get_s3_filepaths import GetS3Files
from ETL.commons.table_query_fcns import get_successful_logged_etl_data_sources

from pyspark.sql.session import SparkSession
from pyspark.sql.dataframe import DataFrame
import os
import shutil
import json
from smart_open import smart_open

from ETL.logging.df_utils.logging_df_utils import GeneralInfoTable


class SchemaReport:
    def __init__(self, unexpected_fields: list = [], missing_expected_fields: list = [], class_name: str = "", data_lineage: dict = {}):
        self.unexpected_fields = unexpected_fields
        self.missing_expected_fields = missing_expected_fields
        self.class_name = class_name
        self.data_lineage = data_lineage

    def get_lineage_path(self):
        if not self.data_lineage:
            return ""
        paths = [self.data_lineage["target_endpoint"] + f"({self.data_lineage['target_type']})"]
        src_endpoints = {k: v for k, v in self.data_lineage.items() if "endpoint" in k and "src" in k}
        src_endpoint_keys = list(src_endpoints.keys())
        src_endpoint_keys.sort()
        paths = paths + [self.data_lineage[_k] + f"({self.data_lineage[_k.replace('endpoint', 'type')]})" for _k in src_endpoint_keys]

        return " <-- ".join(paths)

    def has_fields_report(self):
        return True if self.unexpected_fields + self.missing_expected_fields else False

    def generate_warning_msg(self):
        msg = ""
        if self.unexpected_fields:
            msg += f"Fields present in data file but missing in {self.class_name} schema:\n\n{self.unexpected_fields}"

        if self.missing_expected_fields:
            spacer = "\n\n- # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # - # -\n\n"
            msg += spacer if msg else ""
            msg += f"Fields missing in data file but exists in {self.class_name} schema:\n\n{self.missing_expected_fields}"

        return msg


def collect_s3_paths_within_int_range(env, breadcrumb: str, int_range: int):
    collective_paths = []
    collective_duration_s = 0
    for i in range(int_range):
        get_filepaths = GetS3Files(env=env, breadcrumb=breadcrumb, date_diff=-i)
        paths = get_filepaths.file_paths
        if isinstance(paths, list):
            collective_paths += paths
            collective_duration_s += get_filepaths.duration_sec
    return collective_paths, collective_duration_s


def get_breadcrumb_files(env, breadcrumbs: list, date_diff: int = 0, exact_date: str = "", date_range: dict = None):
    file_paths = []
    paths_n_sizes = []
    get_s3_files_exceptions = []
    duration_s = 0.0
    for breadcrumb in breadcrumbs:
        print(f"Retrieving S3 files for breadcrumb: {breadcrumb}.")
        get_filepaths = GetS3Files(env=env, breadcrumb=breadcrumb, date_diff=date_diff, exact_date=exact_date, date_range=date_range)
        paths = get_filepaths.file_paths
        paths_n_sizes = get_filepaths.paths_n_sizes
        duration_s += get_filepaths.duration_sec

        if isinstance(paths, str):
            get_s3_files_exceptions.append(paths)
        else:
            print(f"{len(paths)} files retrieved.")
            file_paths = file_paths + paths
    return file_paths, paths_n_sizes, get_s3_files_exceptions, duration_s


class GetBreadcrumbFilesHelper:
    def __init__(self, env, breadcrumbs: Union[str, list], date_diff: int = 0, exact_date: str = "", date_range: dict = None, verbose: bool = True):
        self.file_paths = []
        self.paths_n_sizes = []
        self.get_s3_files_exceptions = []
        self.duration_s = 0.0
        self.paths = []
        if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
            self.get_files(env, breadcrumbs, date_diff, exact_date, date_range, verbose)
        else:
            self.paths = "running outside databricks"

    def get_files(self, env, breadcrumbs, date_diff, exact_date, date_range, verbose):
        breadcrumbs = [breadcrumbs] if isinstance(breadcrumbs, str) else breadcrumbs
        for breadcrumb in breadcrumbs:
            if verbose:
                print(f"Retrieving S3 files for breadcrumb: {breadcrumb}.")
            get_filepaths = GetS3Files(env=env, breadcrumb=breadcrumb, date_diff=date_diff, exact_date=exact_date,
                                       date_range=date_range, verbose=verbose)
            self.paths = get_filepaths.file_paths
            self.paths_n_sizes += get_filepaths.paths_n_sizes
            self.duration_s += get_filepaths.duration_sec

            if isinstance(self.paths, str):
                self.get_s3_files_exceptions.append(self.paths)
            else:
                print(f"{len(self.paths)} files retrieved.")
                self.file_paths = self.file_paths + self.paths


def check_for_schema_reports(schema_reports: Union[SchemaReport, List[SchemaReport]] = None):
    has_report = False
    if schema_reports:
        if isinstance(schema_reports, SchemaReport):
            has_report = schema_reports.has_fields_report()
        else:
            has_report = True in [el.has_fields_report for el in schema_reports]

    return has_report


class LoggerHelper:
    def __init__(self, source: Union[str, list], path_n_sizes: list = None):
        _file_paths = "\n".join(source) if isinstance(source, list) else source
        if path_n_sizes:
            _file_sizes = "\n".join([str(el["size"]) for el in path_n_sizes if el["path"] in source])
        else:
            _file_sizes = path_n_sizes

        self.source_n_status = {"data_source": _file_paths, "file_size_byte": _file_sizes}

    def log_status(self, schema_report: Union[SchemaReport, List[SchemaReport]] = None, traceback: str = "", warn: bool = False, failed: bool = False):
        has_schema_report = check_for_schema_reports(schema_report)
        if failed:
            self.source_n_status["status"] = "fail"
            self.source_n_status["traceback"] = traceback
        elif not warn and not has_schema_report and not failed:
            self.source_n_status["status"] = "success"
            self.source_n_status["traceback"] = None if not traceback else traceback
        elif has_schema_report or warn:
            warning_msg = ""
            lineage_header = "\n----- Data Lineage -----\n"
            if schema_report:
                if isinstance(schema_report, SchemaReport) and schema_report.has_fields_report():
                    warning_msg = schema_report.generate_warning_msg()
                    warning_msg += lineage_header + schema_report.get_lineage_path()
                elif isinstance(schema_report, list):
                    warning_msg += "\n\n".join([
                        el.generate_warning_msg() + lineage_header + el.get_lineage_path()
                        for el in schema_report if el.has_fields_report()
                    ])

            self.source_n_status["status"] = "warning"
            self.source_n_status["traceback"] = warning_msg if not traceback else traceback


def filter_out_ingested_datasources(spark: SparkSession, file_paths, etl_data) -> Tuple[list, list]:
    filt_file_paths = []
    ingested_files_exceptions = []
    if file_paths:
        logged_paths = get_successful_logged_etl_data_sources(spark, etl_data)
        for path in file_paths:
            if path in logged_paths:
                ingested_files_exceptions.append(f"already ingested data from:\n   {path}")
            else:
                filt_file_paths.append(path)

        print(ingested_files_exceptions)
        file_paths = filt_file_paths

    return file_paths, ingested_files_exceptions


def get_checkpoint_dir(etl_name: str) -> str:
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        checkpoint_dir = f"/{etl_name}_temp_dir/checkpoints"
    else:
        checkpoint_dir = f"{os.path.abspath('')}/checkpoints"

    return checkpoint_dir


def delete_checkpoint_dir(env: dict, checkpoint_dir: str):
    print("Deleting temp checkpoints dir...")
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        env["dbutils"].fs.rm(checkpoint_dir, recurse=True)
    else:
        shutil.rmtree(checkpoint_dir)


def read_json_file(file_path: str) -> Union[dict, list]:
    f = smart_open(file_path, 'rb')
    json_data = json.load(f)
    f.close()

    return json.loads(json_data) if isinstance(json_data, str) else json.loads(json.dumps(json_data))


def unprocessed_batch_files_filter_log_query(etl_data: str, file_paths_list: list, log_table: str):
    file_path_str = ", ".join([f"'{path}'" for path in file_paths_list])
    return f"""
        select distinct data_source from (
            select explode(split(data_source,'\n')) as data_source from {log_table}
            where etl_data = '{etl_data}' and status != 'fail'
        )
        where data_source in ({file_path_str});
    """


def unprocessed_single_files_filter_log_query(etl_data: str, file_paths_list: list, log_table: str):
    file_path_str = ", ".join([f"'{path}'" for path in file_paths_list])
    return f"""
        select distinct data_source from (
            select data_source from {log_table} where etl_data = '{etl_data}' and status != 'fail'
        )
        where data_source in ({file_path_str});
    """


def remove_logged_processed_files(spark: SparkSession, etl_data_name: str, file_paths: list, batch: bool) -> list:
    if batch:
        data_source_rdd = spark.sql(unprocessed_batch_files_filter_log_query(etl_data_name, file_paths, GeneralInfoTable().table_name)).collect()
    else:
        data_source_rdd = spark.sql(unprocessed_single_files_filter_log_query(etl_data_name, file_paths, GeneralInfoTable().table_name)).collect()

    if len(data_source_rdd) == 0:
        return file_paths
    else:
        processed_files = [row.data_source for row in data_source_rdd]
        unprocessed_files = [path for path in file_paths if path not in processed_files]
        print(f"{len(processed_files)}/{len(file_paths)} were already processed successfully so they have been removed")
        return unprocessed_files


def remove_processed_files(spark: SparkSession, file_paths: list, processed_files_query: str) -> list:
    data_source_rdd = spark.sql(processed_files_query).collect()
    if len(data_source_rdd) == 0:
        return file_paths
    else:
        processed_files = [row.data_source for row in data_source_rdd]
        unprocessed_files = [path for path in file_paths if path not in processed_files]
        print(f"{len(processed_files)}/{len(file_paths)} were already processed successfully so they have been removed")
        return unprocessed_files


def delete_existing_id_rows(spark: SparkSession, df: DataFrame, table_name: str, id_expr: str):
    ids_unq = [f"'{row.id_col}'" for row in df.selectExpr(f"{id_expr} as id_col").distinct().collect()]
    spark.sql(f"delete from {table_name} where {id_expr} in ({', '.join(ids_unq)})")
    time.sleep(2)


def split_files_by_date(file_paths: list) -> dict:
    files_dict = {}
    for path in file_paths:
        path_split = path.split("/")
        date_dict = {"year": path_split[-4], "month": path_split[-3], "day": path_split[-2]}
        file_date = f"{date_dict['year']}-{date_dict['month']}-{date_dict['day']}"
        if file_date in files_dict.keys():
            files_dict[file_date].append(path)
        else:
            files_dict[file_date] = [path]

    return files_dict


def get_env_catalog_name(catalog_name: str):
    os_env = os.getenv("ENV")
    if os_env == "staging":
        os_env = "dev"

    if catalog_name == "hive_metastore":
        return catalog_name
    elif os.environ.get('ISDATABRICKS', 'local') == "TRUE" and os_env != "live":
        catalog_name = f"{os_env}_{catalog_name}"

    return catalog_name


def create_batch_files_json_dataframe(spark: SparkSession, paths: list, print_err: bool = True) -> DataFrame:
    # Load read data from json files into spark dataframe
    try:
        # for json files with all \n and \r characters replaced with " "
        df = spark.read.options(mode="FAILFAST").json(paths)
    except Exception as e:
        if print_err:
            print(f"malformed records found (i.e _corrupt_records columns):\n{str(e)[:400]}")
        # for json files with all \n and \r characters retained
        df = spark.read.json(paths, multiLine=True)
    return df
