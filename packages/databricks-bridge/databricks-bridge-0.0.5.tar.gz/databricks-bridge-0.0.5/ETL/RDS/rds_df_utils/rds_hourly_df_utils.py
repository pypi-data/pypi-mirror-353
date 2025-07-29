from abc import ABC, abstractmethod
import os
from ETL.commons.ease_of_use_fcns import get_checkpoint_dir

db_name = "logging"
checkpoint_dir = get_checkpoint_dir("rds_hourly_integration")


class TablesDynamic(ABC):
    @abstractmethod
    def create_table(self):
        raise NotImplementedError

    @abstractmethod
    def delete_table(self):
        raise NotImplementedError

    @staticmethod
    def get_rds_tables_dict():
        raise NotImplementedError


class RDSConfigTable(TablesDynamic):

    def __init__(self, suffix=""):
        self.table_name = f"{db_name}.rds_table_ingestion_config{suffix}"
        self.permitted_groups = ["analysts"]

    def create_table(self):
        return f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id                          STRING NOT NULL,
            table_name                  STRING NOT NULL,
            table_schema                STRING NOT NULL,
            table_unique_identifier     STRING NOT NULL,
            constant                    BOOLEAN NOT NULL,
            updated_at                  TIMESTAMP NOT NULL,
            dataframe_schema            STRING NOT NULL,
            active                      BOOLEAN NOT NULL
        )
        {"TBLPROPERTIES (DELTA.enableChangeDataFeed = true)" if os.environ.get('ISDATABRICKS', 'local') == "TRUE" else "USING org.apache.spark.sql.parquet"};
        """

    def delete_table(self):
        return f"""DROP TABLE IF EXISTS {self.table_name};"""

    @staticmethod
    def get_rds_tables_dict():
        return [
            {"table_name": "rps_aggregator.client_rps_monitoring",                      "unq_id": "id",                        "constant": True},
        ]
