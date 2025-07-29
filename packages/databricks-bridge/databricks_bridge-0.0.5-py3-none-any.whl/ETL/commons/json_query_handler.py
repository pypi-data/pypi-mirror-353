import json
from pyspark.sql import SparkSession, DataFrame


class JsonQueryHandler:
    def __init__(self):
        self.source_language = "python"

    def get_nested_json_table_df(self, spark: SparkSession, query: str) -> DataFrame:
        """
        :param spark: SparkSession
        :param query: SQL query
        :return: DataFrame
        """
        df_collect = spark.sql(query).collect()
        row_list = []

        for row in df_collect:
            row_dict = {}

            for key, value in row.asDict().items():
                try:
                    row_dict[key] = json.loads(value)
                except Exception as e:
                    row_dict[key] = {} if value == None else str(value)

            row_list.append(row_dict)

        return spark.read.json(spark.sparkContext.parallelize([json.dumps(row_list)]))


'''
from ETL.commons.json_query_handler import JsonQueryHandler
jsonQueryHandler = JsonQueryHandler()

query = """
    select fund_share_class__fund__fund_attributes, fund_share_class__fund__fund_basics
    from loaded.asset_morningstar_xml_isin_dataoutput;
"""
query = "select * from cpd.client;"
df = jsonQueryHandler.get_nested_json_table_df(spark, query)
'''
