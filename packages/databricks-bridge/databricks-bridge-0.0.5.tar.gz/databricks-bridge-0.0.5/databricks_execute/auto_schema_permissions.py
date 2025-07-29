# Databricks notebook source
import importlib
import traceback

from pyspark.sql import SparkSession

from ETL.commons.start_spark_session import get_or_create_spark_session
from ETL.commons.permissions import grant_permissions
from ETL.RDS.rds_df_utils.rds_df_utils import RDSConfigTable
from ETL.logging.logging_decorator_databricks_execute import log_databricks_execute

from databricks_execute.utils.auto_schema_update_table_classes import TableClasses
from databricks_execute.utils.auto_schema_permissions_utils import permissions_list
from databricks_execute.utils.commons import switch_catalog


table_classes = TableClasses().table_classes


def grant_rds_schemas_permissions(spark: SparkSession):
    rds_config_class = RDSConfigTable()
    rds_schemas = list(set([el["table_name"].split(".")[0] for el in rds_config_class.get_rds_tables_dict()]))

    for db_name in rds_schemas:
        spark.sql(f"create database if not exists {db_name};")
        grant_permissions(spark, db_name, rds_config_class.permitted_groups)
    print(f"Granted {rds_config_class.permitted_groups} permissions to all {len(rds_schemas)} rds schemas")


@log_databricks_execute(
    env=locals()
)
def main(env):
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    tables_db_names = []
    data_source_n_status = []
    source_n_status = {"script_path": None}
    schema_permissions_target = f"table_name:"
    for table_class in table_classes:
        table_name = table_class.table_name
        db_name = table_name.split(".")[0]
        schema_permissions_target += db_name
        try:
            switch_catalog(spark, table_class)
        
            if db_name not in tables_db_names:
                spark.sql(f"create database if not exists {db_name};")
                class_module_str = table_class.__module__
                class_src = importlib.import_module(class_module_str)

                if "permitted_groups" in class_src.__dict__.keys():
                    grant_permissions(spark, db_name, class_src.permitted_groups)
                    tables_db_names.append(db_name)
                    print(f"granted prescribed permissions to {db_name} schema\n")

            source_n_status["status"] = "success"
            source_n_status["traceback"] = schema_permissions_target

        except Exception:
            source_n_status["status"] = "fail"
            source_n_status["traceback"] = f"{schema_permissions_target} | {traceback.format_exc()}"

        data_source_n_status.append(source_n_status)

    for dict_el in permissions_list:
        db_name = dict_el["db_name"]
        schema_permissions_target += db_name
        try:
            permitted_groups = dict_el["permitted_groups"]
            if db_name and permitted_groups:
                spark.sql(f"use catalog {dict_el['catalog']};")
                spark.sql(f"create database if not exists {db_name};")
                grant_permissions(spark, db_name, permitted_groups)
                print(f"granted prescribed permissions to {db_name} schema\n")
            source_n_status["status"] = "success"
            source_n_status["traceback"] = schema_permissions_target

        except Exception:
            source_n_status["status"] = "fail"
            source_n_status["traceback"] = f"{schema_permissions_target} | {traceback.format_exc()}"
            
        data_source_n_status.append(source_n_status)

    grant_rds_schemas_permissions(spark)

    return spark, data_source_n_status


if __name__ == "__main__":
    main(locals())
