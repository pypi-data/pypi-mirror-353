from pyspark.sql.session import SparkSession


def get_successful_logged_etl_data_sources(spark: SparkSession, etl_data: str) -> list:
    query = f"""
    with max_date as (
        select max(date_executed) max_date from logging.general_info where etl_data = '{etl_data}'
    )
    select distinct data_source from logging.general_info
    where date_executed = (select * from max_date) and status in ('success', 'warning') and etl_data = '{etl_data}'
    """
    df_data_sources_collect = spark.sql(query).collect()
    logged_data_sources = [row.data_source for row in df_data_sources_collect]

    return logged_data_sources
