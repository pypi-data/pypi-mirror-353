from pyspark.sql.functions import udf, lit
from pyspark.sql.types import DecimalType
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession

def convert(spark: SparkSession, from_currency, to_currency, on_date):
    
    sql_query = f"""
    select a.rate/b.rate as amount
    from 
    (select rate from currency.rate where code ={from_currency} and date = '{on_date}') a,
    (select rate from currency.rate where code = {to_currency} and date = '{on_date}') b
    """

    result = spark.sql(sql_query).collect()
    return print({result[0][0]})

# How to use it
# from pyspark.context import SparkContext
# from pyspark.sql.session import SparkSession
# from ETL.commons.convert_function import convert
# convert(spark, 191 (from_currency), 123(to_currency), '2023-02-15'(on_date))