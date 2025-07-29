from typing import Any

from pandas import DataFrame, Index, Series


def is_a_pandas_dataframe(df: Any) -> bool:
    return isinstance(df, DataFrame)


def pandas_dataframes_are_equal(left: DataFrame, right: DataFrame) -> bool:
    return left.equals(right)


def pandas_series_are_equal(left: Series, right: Series) -> bool:
    return left.equals(right)


def pandas_index_are_equal(left: Index, right: Index) -> bool:
    return left.equals(right)
