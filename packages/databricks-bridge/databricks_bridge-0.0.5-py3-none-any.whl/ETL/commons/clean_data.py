import copy
import humps


def clean_xmltodict_artifacts(dict_data: dict) -> dict:
    artifacts = ["@_", "@", "#"]

    new_dict_data = {}
    changed_keys = []
    for key, val in dict_data.items():
        new_key = key[artifacts.count(key[0]) + artifacts.count(key[:2]):]
        new_key = "Value" if new_key == "text" else new_key

        if key != new_key:
            changed_keys.append(f"{key} -> {new_key}")
        if isinstance(val, dict):
            new_dict_data[new_key] = copy.copy(clean_xmltodict_artifacts(val))
        elif isinstance(val, list):
            for i in range(len(val)):
                if isinstance(val[i], dict):
                    new_dict_data[new_key] = val
                    new_dict_data[new_key][i] = copy.copy(clean_xmltodict_artifacts(val[i]))
        else:
            new_dict_data[new_key] = val

    # if changed_keys:
    #     print(changed_keys)

    return new_dict_data


def clean_csv_col_names(header_line: str, sep: str) -> str:
    columns_list = header_line.split(sep)
    columns_list = [clean_column_name(col_name) for col_name in columns_list]
    columns_list = rename_repeated_col_names(columns_list)
    new_header_line = sep.join(columns_list)
    return new_header_line


def clean_column_name(col_name: str):
    find_n_replace = [
        {"find": '"', "replace": ""},
        {"find": "'", "replace": ""},
        {"find": "\n", "replace": ""},
        {"find": "%", "replace": "_percent_"},
        {"find": "+", "replace": "_plus_"},
        {"find": "&", "replace": "_and_"},
        {"find": ".", "replace": ""},
        {"find": "(", "replace": ""},
        {"find": ")", "replace": ""},
        {"find": ",", "replace": "_"},
        {"find": "/", "replace": "_"},
        {"find": "-", "replace": "_"},
        {"find": " ", "replace": "_"},
        {"find": "__", "replace": "_"},
        {"find": "__", "replace": "_"},
    ]
    col_name = col_name.strip()
    for item in find_n_replace:
        col_name = col_name.replace(item["find"], item["replace"])

    col_name = humps.decamelize(humps.pascalize(col_name)).lower().replace("__", "_")
    # Remove leading and trailing underscores
    if col_name:
        col_name = col_name[:-1] if col_name[-1] == "_" else col_name
        col_name = col_name[1:] if col_name[0] == "_" else col_name

    return col_name


def rename_repeated_col_names(columns_list: list):
    encountered = []
    for i in range(len(columns_list)):
        col_name = columns_list[i]
        if col_name and col_name in encountered:
            columns_list[i] = f"{col_name}_{encountered.count(col_name)}"

        encountered.append(col_name)

    return columns_list
