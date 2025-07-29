# Databricks notebook source

from ETL.commons.start_spark_session import get_or_create_spark_session
from pyspark.sql import SparkSession
from datetime import datetime


def validate_typed_colum(spark: SparkSession, typed_db_name: str, typed_table_name: str, raw_db_name: str, unq_id:str, col_name: str):
    # validation_sql_str = f"""
    #     with typed_tbl as (
    #         select "processed" as tbl, {unq_id}, {col_name} from {typed_db_name}.{typed_table_name}
    #     ), raw_tbl as (
    #         select "raw" as tbl, {unq_id}, {col_name} from {raw_db_name}.{typed_db_name}_{typed_table_name}
    #     ), target_id_tbl as (
    #         select t.{unq_id} from typed_tbl t
    #         left join raw_tbl r on t.{unq_id} = r.{unq_id}
    #         where t.{col_name} is null and nullif(trim(r.{col_name}), "") is not null and t.{col_name} != nullif(trim(r.{col_name}), "")
    #     ), union_tbl as (
    #         select * from typed_tbl
    #         union all
    #         select * from raw_tbl
    #         where {unq_id} in (select {unq_id} from target_id_tbl)
    #     )
    #     select distinct * from union_tbl
    #     order by {col_name}, {unq_id}, tbl
    # """

    validation_sql_str = f"""
        with typed_tbl as (
            select "processed" as tbl, {unq_id} as id, {col_name} as col from {typed_db_name}.{typed_table_name}
        ), raw_tbl as (
            select "raw" as tbl, {unq_id} as id, {col_name} as col from {raw_db_name}.{typed_db_name}_{typed_table_name}
        ), union_tbl as (
            select * from typed_tbl
            union all
            select * from raw_tbl
        ), target_id_tbl as (
            select t.id from typed_tbl t
            left join raw_tbl r on t.id = r.id
            where t.col is null and nullif(trim(r.col), "") is not null and t.col != nullif(trim(r.col), "")
        )
        select distinct tbl, id, col from union_tbl
        where id in (select id from target_id_tbl)
    """
    val_res_collect = spark.sql(validation_sql_str).collect()
    # val_fail_unq_ids = [row[unq_id] for row in val_res_collect if row[unq_id].strip()]
    val_fail_unq_ids = [row.id for row in val_res_collect if row.id.strip()]
    if val_fail_unq_ids:
        print(f"{typed_table_name} validation failure for {col_name} for the following sample {unq_id}: \n{val_fail_unq_ids[:5]}")


def get_unq_id_columns(spark: SparkSession, typed_db_name: str, typed_table_name: str, raw_db_name: str, col_names: list) -> dict:
    full_tbl_v_unq_id_diff_count = {}
    cnt_prefix = "cnt_"
    diff_cnt_prefix = "diff_cnt_"
    # ', '.join(['cnt - '+cnt_prefix+col_name+' as '+diff_cnt_prefix+col_name for col_name in col_names])
    # ', '.join(['try_subtract(cnt, '+cnt_prefix+col_name+') as '+diff_cnt_prefix+col_name for col_name in col_names])
    unq_col_find_sql_str = f"""
        with all_col_unq_cnt_tbl as (
            select count(*) cnt, {', '.join(['count(distinct('+col_name+'))'+' as '+cnt_prefix+col_name for col_name in col_names])}
            from {raw_db_name}.{typed_db_name}_{typed_table_name}
        )
        select {', '.join(['cnt - '+cnt_prefix+col_name+' as '+diff_cnt_prefix+col_name for col_name in col_names])} from all_col_unq_cnt_tbl a
    """
    res_collect = spark.sql(unq_col_find_sql_str).collect()
    for col_name in col_names:
        full_tbl_v_unq_id_diff_count[col_name] = res_collect[0][diff_cnt_prefix+col_name]

    full_tbl_v_unq_id_diff_count_sorted = {key: val for key, val in sorted(full_tbl_v_unq_id_diff_count.items(), key=lambda item: item[1])}

    return full_tbl_v_unq_id_diff_count_sorted


def get_table_names(spark: SparkSession, typed_db_name: str) -> list:
    typed_table_names = [row.tableName for row in spark.sql(f"show tables in {typed_db_name}").collect()]
    raw_table_names = [row.tableName.replace(f"{typed_db_name}_", '') for row in spark.sql(f"show tables in loaded").collect()]
    return [table_name for table_name in typed_table_names if table_name in raw_table_names]


def run_validation(env):
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    # breakpoint()
    typed_db_name = "ms_integration"
    raw_db_name = "loaded"
    typed_table_names = get_table_names(spark, typed_db_name)
    start_time = datetime.now()
    for i, typed_table_name in enumerate(typed_table_names):
        print(f"Validating {i + 1}/{len(typed_table_names)} {typed_table_name}...")

        col_names_collect = spark.sql(f"show columns in {typed_db_name}.{typed_table_name}").collect()
        col_names = [row.col_name for row in col_names_collect]
        # get most unique column
        full_tbl_v_unq_id_diff_count = get_unq_id_columns(spark, typed_db_name, typed_table_name, raw_db_name, col_names)
        unq_id = next(iter(full_tbl_v_unq_id_diff_count))

        print(f"...with {unq_id} as the unique (enough) id on {len(col_names)} columns.")

        for col_name in col_names:
            if col_name != unq_id:
                validate_typed_colum(spark, typed_db_name, typed_table_name, raw_db_name, unq_id, col_name)

    duration_s = (datetime.now() - start_time).total_seconds()
    print(f"Validation duration: {duration_s} seconds")


if __name__ == "__main__":
    run_validation(locals())
