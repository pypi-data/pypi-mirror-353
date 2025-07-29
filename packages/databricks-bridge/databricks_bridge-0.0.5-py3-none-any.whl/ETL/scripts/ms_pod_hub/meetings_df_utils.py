from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ETL.commons.spark_table_utils import create_table_from_schema, non_essentialize_all_other_columns

db_name = "pod_hub"
data_source = {"name": "meetings"}


def get_data_lineage(table_name, kafka_topic):
    return {
        'target_type': "lakehouse",
        'target_endpoint': table_name,
        'src0_type': "s3",
        'src0_endpoint': "landing/ms-pod-hub/MeetingEvent",
        'etl_script_path': "ETL/scripts/ms_pod_hub/meetings_data_etl.py",
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
    def get_spark_schema():
        raise NotImplementedError

    @abstractmethod
    def delete_table(self):
        raise NotImplementedError


class MeetingsTable(TablesDynamic):

    def __init__(self):
        self.table_name = f"{db_name}.{data_source['name']}"
        self.data_lineage = get_data_lineage(self.table_name, kafka_topic="ms-pod-hub.meeting.event")

    def create_table(self):
        return create_table_from_schema(self.table_name, self.get_spark_schema())

    @staticmethod
    def get_spark_schema():
        schema = StructType([
            StructField("id", StringType()),
            StructField("prep_meeting_scheduled", BooleanType()),
            StructField("start_date_time", TimestampType()),
            StructField("end_date_time", TimestampType()),
            StructField("client_user_id", StringType()),
            StructField("pod_id", StringType()),
            StructField("meeting_type", StringType()),
            StructField("meeting_type_detail", StringType()),
            StructField("client_profile_id", StringType()),
            StructField("file_arrival_date", DateType())
        ])
        return non_essentialize_all_other_columns(schema)
    
    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""
