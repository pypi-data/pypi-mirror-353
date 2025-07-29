from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns
from ETL.logging.df_utils.logging_df_utils import GeneralInfoTable

db_name = "pod_hub"
etl_data_name = "task_data_etl"


def get_data_lineage(table_name, kafka_topic):
    return {
        'target_type': "lakehouse",
        'target_endpoint': table_name,
        'src0_type': "s3",
        'src0_endpoint': "landing/ms-pod-hub/TaskEvent",
        'etl_script_path': "ETL/scripts/ms_pod_hub/task_data_etl.py",
        'src1_type': "service",
        'src1_endpoint': "ms-datalake-connector",
        'src1_script_path': "src/main/kotlin/com/ytree/msdatalakeconnector/adapter/driver/kafka/listener/MsPodHubEventListener.kt",
        'src2_type': "kafka",
        'src2_endpoint': kafka_topic,
        'src2_script_path': ""
    }


class TablesDynamic(ABC):
    @abstractmethod
    def create_table(self):
        raise NotImplementedError

    @staticmethod
    def unprocessed_files_filter_query(etl_data: str, file_paths_list: list):
        raise NotImplementedError

    @staticmethod
    def get_spark_schema():
        raise NotImplementedError

    @abstractmethod
    def delete_table_rows(self, ids: list):
        raise NotImplementedError

    @abstractmethod
    def delete_table(self):
        raise NotImplementedError


class TaskDataTable(TablesDynamic):

    def __init__(self):
        self.table_name = f"{db_name}.task_data"
        self.data_lineage = get_data_lineage(self.table_name, kafka_topic="ms-pod-hub.task.event")

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def unprocessed_files_filter_query(etl_data: str, file_paths_list: list):
        log_table = GeneralInfoTable().table_name
        file_path_str = ", ".join([f"'{path}'" for path in file_paths_list])
        return f"""
            select distinct data_source from (
                select explode(split(data_source,'\n')) as data_source from {log_table}
                where etl_data = '{etl_data}' and status = 'success'
            )
            where data_source in ({file_path_str});
        """

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("assignee_id", StringType()),
            StructField("assignee_type", StringType()),
            StructField("client_profile_id", StringType()),
            StructField("category", StringType()),
            StructField("due_date", DateType()),
            StructField("completed_at", TimestampType()),
            StructField("created_at", TimestampType()),
            StructField("high_priority", StringType()),
            StructField("name", StringType()),
            StructField("seen_by_assignee", StringType()),
            StructField("status", StringType()),
        ])
        return non_essentialize_all_other_columns(schema)

    def delete_table_rows(self, task_ids: list):
        ids_str = ", ".join([f"'{id}'" for id in task_ids])
        return f"""DELETE FROM {self.table_name} WHERE id IN ({ids_str});"""

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
