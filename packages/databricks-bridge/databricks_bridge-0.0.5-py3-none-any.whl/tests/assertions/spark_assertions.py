from typing import Any

from chispa.dataframe_comparer import assert_df_equality, assert_schema_equality,DataFramesNotEqualError
from chispa.schema_comparer import SchemasNotEqualError
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType


def is_a_spark_dataframe(df: Any) -> bool:
    return isinstance(df, DataFrame)


def spark_dataframes_are_equal(left: DataFrame, right: DataFrame, **kwargs) -> bool:
    try:
        assert_df_equality(left, right, **kwargs)
    except DataFramesNotEqualError:
        raise DataFramesNotEqualError
    return True


def spark_schemas_are_equal(left: StructType, right: StructType) -> bool:
    try:
        assert_schema_equality(left, right)
    except SchemasNotEqualError:
        raise SchemasNotEqualError
    return True
