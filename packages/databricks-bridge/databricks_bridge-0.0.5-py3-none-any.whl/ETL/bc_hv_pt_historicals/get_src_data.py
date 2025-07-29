from ETL.commons.start_spark_session import get_or_create_spark_session
from databricks_bridge.databricks_bridge import Bridge


def main(env: dict):
    spark, sc, spark_ui_url = get_or_create_spark_session(env)
    bridge = Bridge(hostname="dbc-b23c6dc4-9905.cloud.databricks.com", token="dapi0d5286bc7bae2b02899eb9ccd00ee5e2")
    pd_df, spark_schema = bridge.execute_query("select * from client_financials.statement limit 500")
    print("got pd_df")
    df_spark = bridge.to_spark_df(pd_df, spark_schema)
    spark.sql(f"create database if not exists client_financials;")
    df_spark.write.format("parquet").mode("overwrite").saveAsTable(f"client_financials.statement")
    breakpoint()


if __name__ == "__main__":
    main(locals())
