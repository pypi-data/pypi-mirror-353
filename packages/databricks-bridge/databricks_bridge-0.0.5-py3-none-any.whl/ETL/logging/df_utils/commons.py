import os
import json
import numpy as np
import math
from typing import Union
from smart_open import smart_open

from pyspark.sql import SparkSession, functions as f
from pyspark.sql.dataframe import DataFrame

from alerts.databricks_jobs_slack.databricks_slack_alert import (
    DatabricksSlackAlert, ClientsAlertsSlackAlert, KafkaEventsSchemaChangesSlackAlert
)
from alerts.utils.slack_alert_constants import SlackConstants
from ETL.commons.spark_table_utils import create_dataframe_with_dict_list
from ETL.commons.normalize_data import normalize_dict_data
from ETL.commons.reformat_data import check_for_dict_data_expected_fields
from ETL.commons.spark_table_utils import append_to_table_via_schema_evolution

unappendable_parent_keys = ["data_source_n_status"]
databricks_users = ["databricks@y-tree.com", "it.operations@y-tree.com"]


def extract_etl_files(data_source_n_status: list) -> list:
    files = []
    for source_n_status in data_source_n_status:
        files += source_n_status["data_source"].split("\n")
    return files


def get_past_runs_files_count(spark: SparkSession, etl_data: str, run_cnt: int = 5):
    query = f"""
        select distinct start_time, count(data_source) cnt from (
            select gi_1.etl_data, gi_2.start_time, explode(split(gi_1.data_source,'\n')) as data_source
            from logging.general_info gi_1
            inner join (
                select distinct etl_data, start_time from logging.general_info
                where etl_data='{etl_data}' and data_source_type='datalake'
                and script_path like '/Workspace/Repos/shared/lakehouse/%' and status is not null
                order by start_time desc limit {run_cnt}
            ) gi_2
            on gi_1.etl_data = gi_2.etl_data and gi_1.start_time = gi_2.start_time
        ) group by start_time order by start_time desc;
    """
    return spark.sql(query)


def add_databricks_job_info(env):
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        dbutils = env["dbutils"]
        try:
            notebook_info = json.loads(dbutils.notebook.entry_point.getDbutils().notebook().getContext().toJson())
            return {"notebook_root_id": notebook_info["rootRunId"],
                    "notebook_current_run_id": notebook_info["currentRunId"],
                    "notebook_job_group":  notebook_info["jobGroup"]
                    }
        except:
            return {"notebook_root_id": None, "notebook_current_run_id": None, "notebook_job_group": None}
    else:
        return {"notebook_root_id": None, "notebook_current_run_id": None, "notebook_job_group": None}


def insert_log_into_logging_table(env, spark: SparkSession, table_class, logging_data: dict) -> DataFrame:
    db_name = table_class.table_name.split(".")[0]
    # spark.sql(f"drop database if exists {db_name} cascade;")
    spark.sql(f"create database if not exists {db_name};")
    # Create table is not exist and insert dataframe into table
    spark.sql(table_class.create_table())
    logging_data_full = {**logging_data, **add_databricks_job_info(env)}
    normalized_dict_list = normalize_dict_data(logging_data_full, unappendable_parent_keys)
    logging_table_schema = table_class.get_spark_schema()
    dict_list = [check_for_dict_data_expected_fields(dict_list_el, logging_table_schema) for dict_list_el in normalized_dict_list]
    df = create_dataframe_with_dict_list(spark, dict_list, table_class.get_spark_schema())
    try:
        df.write.insertInto(table_class.table_name, overwrite=False)
        print(f"\nUpdated {table_class.table_name} table")
    except:
        try:
            append_to_table_via_schema_evolution(spark, df, table_class.table_name)
            print(f"\nUpdated {table_class.table_name} table via schema evolution")

        except Exception as e:
            print(f"\n{e}")
            print(f"\nFailed to update {table_class.table_name} table via schema evolution")

    return df


def get_cluster_tags(env, spark: SparkSession):
    all_tags = {"hostname": f'{spark.conf.get("spark.databricks.workspaceUrl").split(".")[0]}'}
    spark_conf_tags = spark.conf.get("spark.databricks.clusterUsageTags.clusterAllTags")
    for tag in json.loads(spark_conf_tags):
        all_tags[tag['key']] = tag['value']

    notebook_job_group = add_databricks_job_info(env)["notebook_job_group"]
    job_id = "" if not notebook_job_group or "job-" not in notebook_job_group else notebook_job_group.split("job-")[1].split("-")[0]
    notebook_path = env["dbutils"].notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    notebook_name = notebook_path.split("/")[-1]
    try:
        notebook_id = env["dbutils"].notebook.entry_point.getDbutils().notebook().getContext().tags().get("notebookId").get()
    except:
        notebook_id = None
    workspace_id = spark.conf.get("spark.databricks.clusterUsageTags.clusterOwnerOrgId")

    notebook_url = "" if job_id else f"https://{all_tags['hostname']}.cloud.databricks.com/?o/{workspace_id}#notebook/{notebook_id}"
    job_url = f"https://{all_tags['hostname']}.cloud.databricks.com/jobs/{job_id}" if job_id else ""
    event_name = f'job: {all_tags["RunName"]} -> {notebook_name}' if job_id else f'notebook: {notebook_name}'

    all_tags["job_id"] = job_id
    all_tags["notebook_path"] = notebook_path
    all_tags["notebook_name"] = notebook_path.split("/")[-1]
    all_tags["notebook_id"] = notebook_id
    all_tags["workspace_id"] = workspace_id
    all_tags["notebook_url"] = notebook_url
    all_tags["job_url"] = job_url
    all_tags["event_name"] = f"{all_tags['environment']} | {event_name}"

    return all_tags


def show_fail_and_warning_logs(env, spark: SparkSession, df: DataFrame, hard_stop: bool = False):
    unsuccessful_logs_df = df.select("*").filter(df.status != "success")
    num_failed_rows = len(unsuccessful_logs_df.collect())
    etl_data = df.select("etl_data").collect()[0].etl_data if "etl_data" in df.columns else ""
    start_time = df.selectExpr("cast(start_time as string) as start_time").collect()[0].start_time

    alert_status = "success"
    if num_failed_rows > 0:
        print("Showing rows with 'fail' and 'warning' status...")
        if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
            env["display"](unsuccessful_logs_df)
        else:
            unsuccessful_logs_df.show(truncate=False)  # show log table

        if unsuccessful_logs_df.select("status").distinct().filter(f.expr("status='fail'")).count() == 0:
            alert_status = "warning"
        else:
            alert_status = "fail"

        if hard_stop and unsuccessful_logs_df.select("*").filter(f.expr("status='fail'")).count() > 0:
            raise Exception("Some failures were logged...")
    else:
        print("No failures or warnings were found!")

    unsuccessful_logs_collect = unsuccessful_logs_df.select("status", "traceback").distinct().collect()
    # msg_dict = {
    #     "warning": [row.traceback for row in unsuccessful_logs_collect if row.status == "warning"],
    #     "fail": [row.traceback for row in unsuccessful_logs_collect if row.status == "fail"],
    # }
    msg_dict = {}
    for row in unsuccessful_logs_collect:
        if row.status in msg_dict.keys():
            msg_dict[row.status].append(row.traceback)
        else:
            msg_dict[row.status] = [row.traceback]

    if os.environ.get('ISDATABRICKS', 'local') == "TRUE" and alert_status != "success":
        current_user = env["dbutils"].notebook.entry_point.getDbutils().notebook().getContext().userName().get()
        if current_user in databricks_users:
            cluster_tags = get_cluster_tags(env, spark)
            cluster_tags["user"] = current_user
            send_slack_alert(env, cluster_tags, alert_status, etl_data=etl_data, message=msg_dict, start_time=start_time)


def trigger_files_discrepancy_alert(env, spark, etl_files: list, df_file_cnt: DataFrame):
    len_cur_files = len(etl_files)
    df_file_cnt_collect = df_file_cnt.collect()
    mean_file_count = 1 if len(df_file_cnt_collect) <= 1 else np.round(np.mean([int(row.cnt) for row in df_file_cnt_collect]), 2)
    percentage_cnt = round((len_cur_files/math.floor(mean_file_count)) * 100, 2)
    min_thresh = 80.0
    if percentage_cnt < min_thresh:
        current_user = env["dbutils"].notebook.entry_point.getDbutils().notebook().getContext().userName().get()
        if current_user in databricks_users:
            cluster_tags = get_cluster_tags(env, spark)
            cluster_tags["user"] = current_user
            df_show_str = df_file_cnt._jdf.showString(20, int(False), False)
            status_params = SlackConstants().status_params
            msg = status_params["files_count_check"]["message"].format(
                cur_file_cnt=len_cur_files, prev_cnt_mean=mean_file_count, df_show_string=df_show_str,
                num_runs=df_file_cnt.count(), percentage_cnt=percentage_cnt, max_decrease_threshold=100-min_thresh
            )
            send_slack_alert(env, cluster_tags, "files_count_check", message=msg)


def send_slack_alert(env, cluster_tags: dict, status: str, etl_data: str = "", message: Union[dict, str] = "", start_time: str = ""):
    job_status = status
    src_url = cluster_tags["job_url"] if cluster_tags["job_url"] else cluster_tags["notebook_url"]
    if cluster_tags["environment"] == "live":
        if etl_data == "kafka_schema_checks":
            log_query = f"select * from logging.general_info where etl_data = '{etl_data}' and start_time::string = '{start_time}' and status = 'warning';"
            title = f"{cluster_tags['environment']} | Kafka Events Schema Checks:"
            msg = {k: v for k, v in message.items() if k == "warning"}
            KafkaEventsSchemaChangesSlackAlert(env=env, title=title, schema_reports=msg, log_query=log_query)

        msg = message if etl_data != "kafka_schema_checks" else None if "fail" not in message.keys() else {k: v for k, v in message.items() if k == "fail"}
        if msg:
            DatabricksSlackAlert(
                env=env, title=cluster_tags["event_name"], status=job_status, user=cluster_tags["user"], src_url=src_url,
                message=msg
            )


def replace_email_with_slack_user(string: str):
    email_to_slack_user = {
        "ed@y-tree.com": "@Ed", "sejal@y-tree.com": "@Sejal", "salbih@y-tree.com": "@Salbih", "jai@y-tree.com": "@Jai",
        "tiago@y-tree.com": "@Tiago", "tiffany@y-tree.com": "@Tiffany McGee", "monika@y-tree.com": "@Monika",
        "hoa@y-tree.com": "@Hoa", "arielle@y-tree.com": "@Arielle", "marjan@y-tree.com": "@Marjan",

        "databricks@y-tree.com": "@titan", "mat.shephard@y-tree.com": "@Mat", "arsa@y-tree.com": "@Arsa",
        "saeed@y-tree.com": "@Saeed"
    }
    for email, slack_user in email_to_slack_user.items():
        string = string.replace(email, slack_user.lower())

    return string


def generate_downstream_clients(table_name, catalog: str):
    _f = smart_open("/dbfs/FileStore/data_lineage/data_lineage_running_queries.json")
    dict_list = json.load(_f)
    impacted_queries = [el for el in dict_list if table_name.lower() in [tbl.replace(f"{catalog}.", "").lower() for tbl in el["tables_used"]]]
    downstream_clients = []
    for el in impacted_queries:
        data = f"*query_id*: {el['query_id']},\n*query_name*: {el['query_name']},\n*run_as*: {el['executed_as_user_name']},\n*query*: ```{el['query_text_cleaned'][:100]}...```"
        downstream_clients.append(data)

    return "\n\n".join(downstream_clients)


def send_table_clients_alert(env: dict, spark: SparkSession, table_name: str, catalog: str = "hive_metastore"):
    current_user = env["dbutils"].notebook.entry_point.getDbutils().notebook().getContext().userName().get()
    if current_user in databricks_users:
        cluster_tags = get_cluster_tags(env, spark)
        src_url = cluster_tags["job_url"] if cluster_tags["job_url"] else cluster_tags["notebook_url"]
        if cluster_tags["environment"] == "live":
            msg = generate_downstream_clients(table_name, catalog)
            msg = replace_email_with_slack_user(msg)
            title = cluster_tags["event_name"]
            if msg.strip():
                ClientsAlertsSlackAlert(env=env, title=title, table_name=table_name, message=msg, src_url=src_url)
