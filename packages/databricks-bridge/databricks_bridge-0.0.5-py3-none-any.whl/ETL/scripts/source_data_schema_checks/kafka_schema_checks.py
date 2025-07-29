# Databricks notebook source
import os
import random
import traceback
import json
from datetime import date, timedelta

from pyspark.sql import SparkSession, DataFrame

from databricks_execute.utils.auto_schema_update_table_classes import TableClasses
from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.ease_of_use_fcns import GetBreadcrumbFilesHelper, LoggerHelper, create_batch_files_json_dataframe
from ETL.commons.set_logger_level import set_logger_level_error
from ETL.logging.logging_decorators import log_general_info


set_logger_level_error(locals())
script_path = f"{os.path.abspath('')}/kafka_schema_checks.py"


def get_source_files(env, breadcrumb, date_diff=0):
    file_helper = GetBreadcrumbFilesHelper(env, [breadcrumb], date_diff=date_diff, verbose=False)

    return file_helper


def get_all_breadcrumbs():
    table_classes = [
        table_class for table_class in TableClasses().table_classes
        if hasattr(table_class, "data_lineage") and
           "src1_endpoint" in table_class.data_lineage.keys() and
           table_class.data_lineage["src1_endpoint"] == "ms-datalake-connector" and
           "kafka" in table_class.data_lineage["src1_type"]
    ]
    breadcrumbs = list(set([table_class.data_lineage["src0_endpoint"] for table_class in table_classes]))
    return breadcrumbs


def get_most_recent_files(env, breadcrumb, date_diff=0):
    print(f"Retrieving S3 files for breadcrumb: {breadcrumb}...")
    most_recent_files = []
    current_date = date.today()
    start_date = (current_date - timedelta(days=abs(date_diff))).strftime("%Y-%m-%d")
    for i in range(5):
        date_diff += -i
        most_recent_files = get_source_files(env, breadcrumb, date_diff).file_paths
        if most_recent_files:
            break

    end_date = (current_date - timedelta(days=abs(date_diff))).strftime("%Y-%m-%d")
    if not most_recent_files:
        print(f"There are no files for the past 5 days between {start_date} and {end_date} for the breadcrumb:\n\t{breadcrumb}")

    return most_recent_files, date_diff


def get_breadcrumb_files(env, breadcrumb):
    print(f"\nRetrieving most recent S3 files for breadcrumb: {breadcrumb}...")
    most_recent_files, date_diff = get_most_recent_files(env, breadcrumb)
    print(f"Retrieving past S3 files for breadcrumb: {breadcrumb}...")
    past_files, _ = get_most_recent_files(env, breadcrumb, date_diff - 4)
    # most_recent_files = [path for path in most_recent_files if path.split(".")[-1] != "xml"]
    most_recent_files = [path for path in most_recent_files if path.split(".")[-1] == "json"]
    past_files = [path for path in past_files if path.split(".")[-1] == "json"]

    return most_recent_files, past_files


def create_dataframe(spark: SparkSession, file_paths: list, file_type: str, shuffle: bool=False):
    if shuffle:
        random.shuffle(file_paths)

    if file_type == "json":
        return create_batch_files_json_dataframe(spark, file_paths[:1000], print_err=False)


def get_updated_fields(recent_schema, past_schema):
    updated_fields = []
    for field_schema in recent_schema:
        past_field_schema = [el for el in past_schema if el.name == field_schema.name][0]
        if past_field_schema and field_schema != past_field_schema:
            updated_field = {"new_updates": str(field_schema), "past_field_schema": str(past_field_schema)}
            updated_fields.append(updated_field)

    return updated_fields


def collect_tree_paths(df: DataFrame):
    schema_tree = df._jdf.schema().treeString().replace("root\n", "")
    schema_tree_list = schema_tree.split("\n")
    field_paths = []
    for i, el in enumerate(schema_tree_list):
        if len(schema_tree_list) > i+1 and schema_tree_list[i+1].count("|") <= el.count("|"):
            parent_branches = []
            cur_branch_fork_num = el.count("|")
            # for j in range(len(schema_tree_list[:i]), 0, -1):
            for j in reversed(schema_tree_list[:i]):
                if j.count("|") < cur_branch_fork_num:
                    parent_branches = [j] + parent_branches
                    cur_branch_fork_num = j.count("|")

            path = parent_branches + [el]
            path = [_el.replace("|", "").replace("--", "").strip() for _el in path]
            field_paths.append(path)

    return field_paths


def get_path_diffs(cur_paths, past_paths):
    fields_report = {"new": [], "removed": [], "updated": []}
    for path in cur_paths:
        name_only_path = [el.split(":")[0] for el in path]
        past_name_only_paths = [[el.split(":")[0] for el in _path] for _path in past_paths]

        if name_only_path not in past_name_only_paths:
            fields_report["new"].append(" -> ".join(path))
        elif path not in past_paths:
            prev_path = [_path for _path in past_paths if [el.split(":")[0] for el in _path] == name_only_path][0]
            report = {"current": " -> ".join(path), "previous": " -> ".join(prev_path)}
            fields_report["updated"].append(report)

    for path in past_paths:
        name_only_path = [el.split(":")[0] for el in path]
        current_name_only_paths = [[el.split(":")[0] for el in _path] for _path in cur_paths]
        if name_only_path not in current_name_only_paths:
            fields_report["removed"].append(" -> ".join(path))

    return fields_report


def check_kafka_schema(spark, breadcrumb, most_recent_files, past_files, file_filter=None):
    if file_filter:
        most_recent_files = [path for path in most_recent_files if file_filter in path]
        past_files = [path for path in past_files if file_filter in path]

    if not most_recent_files or not past_files:
        return

    recent_df = create_dataframe(spark, most_recent_files, "json")
    past_df = create_dataframe(spark, past_files, "json", shuffle=True)
    recent_schema = recent_df.schema
    past_schema = past_df.schema

    if recent_schema != past_schema:
        print(f"there has been a change in schema for breadcrumb:\n\t{breadcrumb}\n")
        recent_paths = collect_tree_paths(recent_df)
        past_paths = collect_tree_paths(past_df)
        fields_reports = get_path_diffs(recent_paths, past_paths)
        get_date_from_path = lambda path: path.split(breadcrumb+"/")[1][:10].replace("/", "-")
        check_report = {
            "breadcrumb": breadcrumb,
            "file_filter": file_filter,
            "new_fields": fields_reports["new"],
            "removed_fields": fields_reports["removed"],
            "updated_fields": fields_reports["updated"],
            "recent_schema": str(recent_schema), "past_schema": str(past_schema),
            "recent_files": most_recent_files[:10], "past_files": past_files[:10],
            "recent_files_date": get_date_from_path(most_recent_files[0]),
            "past_files_date": get_date_from_path(past_files[0]),
        }
        return json.dumps(check_report, indent=4)
    else:
        print("\tMost recent schema matches with past schema\n")
    return None


def trigger_checks(spark, breadcrumb, most_recent_files, past_files, file_filter):
    logger_helper = LoggerHelper(source=json.dumps({"src": breadcrumb, "filter": file_filter}))
    try:
        check_report = check_kafka_schema(spark, breadcrumb, most_recent_files, past_files, file_filter=file_filter)
        if check_report:
            logger_helper.log_status(traceback=check_report, warn=True)
        else:
            logger_helper.log_status()
    except Exception as e:
        logger_helper.log_status(traceback=traceback.format_exc(), failed=True)

    return logger_helper


@log_general_info(
    env=locals(),
    etl_data="kafka_schema_checks",
    script_path=script_path,
    data_sources_type="datalake"
)
def run_checks(env):
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    breadcrumbs = get_all_breadcrumbs()

    data_source_n_status = []
    for breadcrumb in breadcrumbs:
        most_recent_files, past_files = get_breadcrumb_files(env, breadcrumb)

        if breadcrumb == "landing/asset/ms_asset":
            file_filters = list(set(["|" + path.split("|")[-1] for path in most_recent_files]))
            for file_filter in file_filters:
                logger_helper = trigger_checks(spark, breadcrumb, most_recent_files, past_files, file_filter)
                data_source_n_status.append(logger_helper.source_n_status)
        else:
            logger_helper = trigger_checks(spark, breadcrumb, most_recent_files, past_files, None)
            data_source_n_status.append(logger_helper.source_n_status)

    return spark, data_source_n_status, 0.0


if __name__ == "__main__":
    run_checks(locals())
