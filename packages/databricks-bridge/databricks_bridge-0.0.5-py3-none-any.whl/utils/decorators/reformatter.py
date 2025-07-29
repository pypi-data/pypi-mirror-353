from datetime import datetime
import functools
from decimal import Decimal

from humps import camelize
from pyspark.sql.types import StructType


def convert_date_strings(table_schema: StructType, camel_case: bool = False):
    """
    :param table_schema: the schema of your spark dataframe. These fields should reflect the data you are sending in.
    :param camel_case: state whether the data you are sending in has camelCase keys. This is relevant because all our
    spark schemas should be in snake_case. But we need this check if the original data is in camelCase and we need to
    preserve that to access data.

    Reformat all the date/time related values of your data to a suitable python datetime format.
    Only works on flattened structures.
    Make sure you are only using this decorator on a single flattened dictionary that represents a table row.
    """

    def _pre_process_date_times(*args, **kwargs):
        if camel_case:
            date_time_columns = [(camelize(x.get('name')), x.get('type')) for x in table_schema.jsonValue()['fields']
                                 if x.get('type') in ['timestamp', 'date']]
        else:
            date_time_columns = [(x.get('name'), x.get('type')) for x in table_schema.jsonValue()['fields']
                                 if x.get('type') in ['timestamp', 'date']]
        data = args[0]
        for column in date_time_columns:
            if isinstance(data[column[0]], str) and column[1] == 'timestamp':
                data[column[0]] = datetime.strptime(data[column[0]][:23], "%Y-%m-%dT%H:%M:%S.%f")
            elif isinstance(data[column[0]], str) and column[1] == 'date':
                data[column[0]] = datetime.strptime(data[column[0]], '%Y-%m-%d')
        return data

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(_pre_process_date_times(*args, **kwargs))
        return wrapper

    return decorator


def convert_decimal_strings(table_schema: StructType, camel_case: bool = False):
    """
    :param table_schema: the schema of your spark dataframe. These fields should reflect the data you are sending in.
    :param camel_case: state whether the data you are sending in has camelCase keys. This is relevant because all our
    spark schemas should be in snake_case. But we need this check if the original data is in camelCase and we need to
    preserve that to access data.

    Reformat all the decimal related values of your data to a suitable python Decimal format.
    Only works on flattened structures.
    Make sure you are only using this decorator on a single flattened dictionary that represents a table row.
    """

    def _pre_process_decimals(*args, **kwargs):
        if camel_case:
            decimal_columns = [camelize(x.get('name')) for x in table_schema.jsonValue()['fields']
                               if 'decimal' in x.get('type')]
        else:
            decimal_columns = [x.get('name') for x in table_schema.jsonValue()['fields']
                               if 'decimal' in x.get('type')]
        data = args[0]
        for column in decimal_columns:
            data[column] = Decimal(str(data[column])) if data[column] is not None else None
        return data

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(_pre_process_decimals(*args, **kwargs))
        return wrapper

    return decorator
