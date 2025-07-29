import pandas as pd
from pandas.core.frame import DataFrame as pd_DataFrame
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import arrays_zip, explode
from pyspark.sql import functions as f
import numpy as np
import copy
import humps
from typing import Tuple
import time


def normalize_dict_data(dict_data: dict, unappendable_parent_keys: list) -> list:
    # print("Normalising file data...")
    # start_time = time.time()

    def recur(dict_data: dict):
        dict_list = []
        new_dict_data = dict_data
        # unappendable_parent_keys = ["rows", "collection", "history", "rowInfo", "transactions"]
        nested_keys = [k for k in dict_data.keys() if isinstance(dict_data[k], dict) or isinstance(dict_data[k], list)]

        if nested_keys:
            for key in nested_keys:
                new_key_prefix = humps.decamelize(key + "_") if key not in unappendable_parent_keys else ""

                if isinstance(dict_data[key], dict):
                    temp_dict = {}
                    for k, v in dict_data[key].items():
                        new_key = new_key_prefix + humps.decamelize(k)
                        temp_dict[new_key.lower()] = v

                    new_dict_data.update(temp_dict)
                    del new_dict_data[key]
                    dict_list.append(copy.copy(new_dict_data))

                elif isinstance(dict_data[key], list):
                    temp_list = []
                    for el in dict_data[key]:
                        temp_dict = {}
                        if isinstance(el, dict):
                            for k, v in el.items():
                                new_key = new_key_prefix + humps.decamelize(k)
                                temp_dict[new_key.lower()] = v

                            new_dict_data.update(temp_dict)
                            temp_list.append(temp_dict)

                        elif isinstance(el, list):
                            for v in el:
                                temp_list.append(v)

                    del new_dict_data[key]
                    if temp_list:
                        for el in temp_list:
                            new_dict_data.update(el)
                            dict_list.append(copy.copy(new_dict_data))
                    else:
                        dict_list.append(copy.copy(new_dict_data))

            new_dict_list = []
            for el in dict_list:
                new_dict_el = copy.copy(recur(el))
                for new_el in new_dict_el:
                    new_dict_list = new_dict_list + [new_el] if new_el not in new_dict_list else new_dict_list

            dict_list = new_dict_list if new_dict_list else dict_list

        else:
            dict_list = [dict_data] if isinstance(dict_data, dict) else dict_data

        return dict_list

    dict_list = recur(dict_data)
    # print("Finished normalisation...")
    # print(f"Duration: {time.time() - start_time} seconds\n")
    return dict_list


def normalize_dict_with_pd(dict_data: dict) -> list:
    # print("Normalising file data...")
    # start_time = time.time()
    root_df = pd.json_normalize(dict_data)

    def sjoin(x):
        return ';'.join(x[x.notnull()].astype(str))

    def dedupe_df(df):
        rows_cols = list(df.columns)
        duped_cols = list(set([x for x in rows_cols if rows_cols.count(x) > 1]))
        if duped_cols:
            rm_dupe_cols = df.drop(duped_cols, axis=1)
            dupe_df = df[duped_cols]
            deduped_df = dupe_df.groupby(level=0, axis=1).apply(lambda x: x.apply(sjoin, axis=1))
            df = pd.concat([rm_dupe_cols, deduped_df], axis=1)

        return df

    def recur(root_df: pd_DataFrame) -> pd_DataFrame:

        all_rows = ""
        for i in range(len(root_df)):  # looping through each row
            row_df = pd.DataFrame(root_df.loc[i]).T
            # collect all columns with list data types
            cols_2_drop = []
            for col in row_df.columns:
                if isinstance(root_df.iloc[i][col], list) and isinstance(root_df.iloc[i][col][0], dict):
                    cols_2_drop.append(col)

            if not cols_2_drop:
                return root_df

            # normalize df columns with list data
            for col in cols_2_drop:
                # print(f"dropping column {col} on row {i}")

                # drop cols with list data from row_df
                new_row_df = row_df.drop([col], axis=1)
                # expand the list data into individual rows
                next_row_df = pd.json_normalize(row_df.iloc[0][col])
                # rename new expanded list dataframe to preserve parent list column name
                col_rename_dict = {}
                [col_rename_dict.update({el: col + "_" + el.replace(".", "_")}) for el in list(next_row_df.columns)]
                next_row_df.rename(columns=col_rename_dict, inplace=True)
                # duplicate the non-list type column dataframes to match number of rows in the expanded list df
                match_row_str = "pd.concat([" + ('new_row_df,' * len(next_row_df))[:-1] + "]).reset_index(drop=True)"
                dup_root_row_df = eval(match_row_str)
                # concatenate the duplicated and expanded dataframes together to form new normalized dataframe
                new_root_row_df = pd.concat([dup_root_row_df, next_row_df], axis=1)

            # collect all normalized df into df data rows
            if type(all_rows) == pd.core.frame.DataFrame:
                all_rows = dedupe_df(all_rows)
                new_root_row_df = dedupe_df(new_root_row_df)
                all_rows = pd.concat([copy.copy(all_rows), copy.copy(new_root_row_df)]).reset_index(drop=True)
            else:
                all_rows = copy.copy(new_root_row_df)

        return recur(copy.copy(all_rows))

    normalized_pd_df = recur(root_df)
    normalized_pd_df = normalized_pd_df.replace({np.nan: None}) #replace NaN with None
    # print("Finished normalisation...")
    # print(f"Duration: {time.time() - start_time} seconds\n")

    return list(rename_normalized_pd_df(normalized_pd_df).T.to_dict().values())


def decamelize_df_cols(df: DataFrame) -> DataFrame:
    col_renamed = [f"{col_name} as {humps.decamelize(col_name).replace('__', '_')}" for col_name in df.columns]
    df = df.selectExpr(col_renamed)
    return df


def rename_normalized_pd_df(normalized_pd_df):
    # rename and decamelize pandas df
    col_rename_dict = {}
    [col_rename_dict.update({el: humps.decamelize(el.replace(".", "_")).replace("__", "_")}) for el in
     list(normalized_pd_df.columns)]
    normalized_pd_df.rename(columns=col_rename_dict, inplace=True)

    return normalized_pd_df


def normalize_dict_only_with_pd(dict_data: dict) -> list:
    root_df = pd.json_normalize(dict_data)
    root_df = root_df.replace({np.nan: None}) #replace NaN with None

    return list(rename_normalized_pd_df(root_df).T.to_dict().values())


def get_dict_key_paths(dict_data: dict, dict_n_list: bool) -> list:
    def recur(sub_dict_data: dict, all_keys=[]) -> list:
        key_list = []
        if isinstance(sub_dict_data, dict):
            for k, v in sub_dict_data.items():
                if isinstance(v, dict):
                    key_list += recur(v, all_keys+[k])
                elif isinstance(v, list) and dict_n_list:
                    for i, el in enumerate(v):
                        key_list += recur(el, all_keys+[k, i])
                else:
                    key_list.append(all_keys+[k])
        elif isinstance(sub_dict_data, list):
            for i, el in enumerate(sub_dict_data):
                key_list += recur(el, all_keys + [i])
        return key_list
    return recur(dict_data)


def get_nested_df_paths(df: DataFrame, nested_children=[]) -> Tuple[list, list]:

    def recur(df_json_schema, cur_col_name, query_paths):
        df_field_schemas = df_json_schema["fields"]
        next_nest_cols = []
        for field_schema in df_field_schemas:
            field_name = field_schema["name"]
            field_name = cur_col_name if field_name in cur_col_name else field_name
            field_type = field_schema["type"]
            if isinstance(field_type, dict):
                field_type_type = field_type["type"]

                if field_type_type == "array" and isinstance(field_type["elementType"], dict):
                    field_type_element_type = field_type["elementType"]
                    needs_index = True if field_type_element_type["type"] == "array" else False
                    if needs_index:
                        array_fields = field_type_element_type["elementType"]["fields"]
                        next_nest_cols = [f"{field_name}[0].{nested_field['name']}" for nested_field in array_fields]
                    else:
                        struct_fields = field_type_element_type["fields"]
                        next_nest_cols = [f"{field_name}.{nested_field['name']}" for nested_field in struct_fields]

                elif field_type_type == "struct":
                    struct_fields = field_type["fields"]
                    next_nest_cols = [f"{field_name}.{nested_field['name']}" for nested_field in struct_fields]

                query_paths += next_nest_cols

                for col in next_nest_cols:
                    query_paths = copy.copy(recur(df.selectExpr(col).schema.jsonValue(), col, query_paths))

        return query_paths

    all_query_paths = recur(df.schema.jsonValue(), "", [])
    nested_children_paths = [query_path for query_path in all_query_paths for child in nested_children if
                            child in query_path]

    return all_query_paths, nested_children_paths


def explode_df_level_by_array_level(df: DataFrame, base_unq_id: str, base_array_path: str) -> DataFrame:
    array_levels = [array_level for array_level in base_array_path.split("[0]")]
    df_base = df
    cur_unq_id = base_unq_id
    for array_level in array_levels:
        unq_id_type = df_base.selectExpr(cur_unq_id).schema[0].jsonValue()["type"]
        unq_id_expr = f"{cur_unq_id} as {cur_unq_id.replace('.', '_')}"
        if array_level != array_levels[0]:
            array_level_clean = array_level.replace('.', '')
            nested_col_expr = [f"{col}.{array_level_clean} as {col}_{array_level_clean}" for col in df_base.columns if col != cur_unq_id][0]
        else:
            nested_col_expr = f"{array_level} as {array_level.replace('.', '_')}"

        df_base = df_base.selectExpr(unq_id_expr, nested_col_expr)
        arrays_zip_args_list = []
        for col in df_base.columns:
            str_arg = f"'{col}'"
            if col != cur_unq_id:
                arrays_zip_args_list.append(str_arg)
            else:
                if isinstance(unq_id_type, dict):
                    arrays_zip_args_list.append(str_arg)

        arrays_zip_args = ", ".join(arrays_zip_args_list)
        explosion_select_expression = [f"{'tmp.' + col if col in arrays_zip_args else col}" for col in df_base.columns]
        normalized_df = df_base.withColumn("tmp", eval(f"arrays_zip({arrays_zip_args})")).withColumn("tmp", explode("tmp")).selectExpr(explosion_select_expression)
        df_base = normalized_df
        cur_unq_id = unq_id_expr.split(" ")[-1]

    return df_base


def unnest_df(nested_df: DataFrame, nested_fields: dict) -> DataFrame:
    """
    :param df:
        sample df schema:
            root
             |-- cashBuffer: struct (nullable = true)
             |    |-- amount: double (nullable = true)
             |    |-- ccy: long (nullable = true)
             |-- totalHeldsInAccounts: struct (nullable = true)
             |    |-- amounts: array (nullable = true)
             |    |    |-- element: struct (containsNull = true)
             |    |    |    |-- amount: double (nullable = true)
             |    |    |    |-- ccy: long (nullable = true)
             |    |-- total: struct (nullable = true)
             |    |    |-- amount: double (nullable = true)
             |    |    |-- ccy: long (nullable = true)
    :param nested_fields:
        sample nested_fields dict config
            {
                "cashBuffer": {"amount": None, "ccy": None},
                "totalHeldsInAccounts": {"amounts": None, "total": {"amount": None, "ccy": None}}
            }
        dict keys with None values will stop its unnesting at that point
        dict keys with dict values will continue to unnest further into the next nested fields
    :return: df
        sample return df schema:
            root
             |-- cash_buffer_amount: double (nullable = true)
             |-- cash_buffer_ccy: long (nullable = true)
             |-- totalHeldsInAccounts_amounts: array (nullable = true)
             |    |-- element: struct (containsNull = true)
             |-- total_helds_in_accounts_amounts: array (nullable = true)
             |    |-- element: struct (containsNull = true)
             |    |    |-- amount: double (nullable = true)
             |    |    |-- ccy: long (nullable = true)
             |-- total_helds_in_accounts_total_amount: double (nullable = true)
             |-- total_helds_in_accounts_total_ccy: long (nullable = true)
             |-- total_helds_in_accounts_total_amount: double (nullable = true)
             |-- total_helds_in_accounts_total_ccy: long (nullable = true)
    """
    nested_df_cols = nested_df.columns

    def recur(df: DataFrame, nested_fields) -> DataFrame:
        if nested_fields is None:
            return df

        for nested_col_name, val in nested_fields.items():
            if val and df.selectExpr(f"{nested_col_name}").filter(f"{nested_col_name} is not null").count() != 0:
                nested_cols = df.select(f"{nested_col_name}.*").schema.names
                nested_cols = [col_name for col_name in nested_cols if col_name not in nested_df_cols and humps.camelize(f"{humps.decamelize(nested_col_name)}_{humps.decamelize(col_name)}") not in nested_df_cols]
                select_str_list = [f"{nested_col_name}.{col_name} as {humps.decamelize(nested_col_name)}_{humps.decamelize(col_name)}" for col_name in nested_cols]
                df = df.selectExpr(["*"] + select_str_list).drop(nested_col_name)

                if val is not None:
                    new_nested_fields = {}
                    for key, v in val.items():
                        new_nested_fields[f"{humps.decamelize(nested_col_name)}_{humps.decamelize(key)}"] = v

                    df = recur(df, new_nested_fields)
        return df

    return recur(nested_df, nested_fields)


def explode_array_col(df: DataFrame, target_col: str):
    select_list = [_col if _col != target_col else f.explode_outer(_col).alias(_col) for _col in df.columns]
    return df.select(select_list).distinct()


def unnest_array_struct_df(df: DataFrame, table_nested_fields, unappendable_parent_keys: list = []) -> DataFrame:
    df_cols = df.columns

    def recur(df: DataFrame, nested_fields) -> DataFrame:
        if nested_fields is None:
            return df

        # find and explode all arrays first
        array_cols = [_col for _col, v in nested_fields.items() if isinstance(v, list)]
        for arr_col in array_cols:
            df = explode_array_col(df, arr_col)
            nested_fields[arr_col] = nested_fields[arr_col][0]

        for nested_col_name, val in nested_fields.items():
            if nested_col_name not in df.columns or val is None:
                continue

            non_null_row_cnt = df.selectExpr(f"{nested_col_name}").filter(f"{nested_col_name} is not null").count()
            if nested_col_name in df.columns and non_null_row_cnt != 0:
                if df.schema[nested_col_name].dataType.typeName() == "array":
                    df = explode_array_col(df, nested_col_name)

                nested_cols = df.selectExpr(f"{nested_col_name}.*").schema.names
                if nested_col_name not in unappendable_parent_keys:
                    nested_cols = [col_name for col_name in nested_cols if humps.camelize(f"{humps.decamelize(nested_col_name)}_{humps.decamelize(col_name)}") not in df_cols]
                    select_str_list = [f"{nested_col_name}.{col_name} as {humps.decamelize(nested_col_name)}_{humps.decamelize(col_name)}" for col_name in nested_cols]
                else:
                    nested_cols = [col_name for col_name in nested_cols if humps.camelize(f"{humps.decamelize(col_name)}") not in df_cols]
                    select_str_list = [f"{nested_col_name}.{col_name} as {humps.decamelize(col_name)}" for col_name in nested_cols]

                df = df.selectExpr(["*"] + select_str_list).drop(nested_col_name)

                if val is not None:
                    new_nested_fields = {}
                    for key, v in val.items():
                        if nested_col_name not in unappendable_parent_keys:
                            new_nested_fields[f"{humps.decamelize(nested_col_name)}_{humps.decamelize(key)}"] = v
                        else:
                            new_nested_fields[humps.decamelize(key)] = v
                    df = recur(df, new_nested_fields)
        return df

    return recur(df, table_nested_fields)
