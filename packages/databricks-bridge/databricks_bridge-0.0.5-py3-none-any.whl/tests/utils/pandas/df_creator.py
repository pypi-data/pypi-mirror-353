from typing import List, Any

import pandas as pd
from pandas import DataFrame

from tests.exceptions import TestingException


def create_pandas_dataframe(
        column_names: List,
        *rows: List[Any]
) -> DataFrame:
    try:
        data_rows = [[row[i] for row in rows] for i, _ in enumerate(rows[0])]
        dataframe = pd.DataFrame.from_dict(dict(zip(column_names, data_rows)))
    except IndexError as e:
        raise IndexError(f"Make sure your row data is all equal length. Error: {e}")
    except Exception as e:
        raise TestingException(f"Something has gone wrong: {e}")

    return dataframe
