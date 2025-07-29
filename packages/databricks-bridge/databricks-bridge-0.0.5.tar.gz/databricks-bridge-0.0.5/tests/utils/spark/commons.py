from typing import List

from pyspark.sql import DataFrame


def get_column_names(df: DataFrame) -> List:
    return [field.name for field in df.schema.fields]


def get_nth_row(df: DataFrame, n: int) -> List:
    try:
        return list(df.collect()[n].asDict().values())
    except IndexError:
        raise IndexError("Accessing row number which is not available in dataframe")
