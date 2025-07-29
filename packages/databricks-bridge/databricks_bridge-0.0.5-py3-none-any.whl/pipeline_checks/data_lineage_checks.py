import json

from databricks_execute.utils.auto_schema_update_table_classes import TableClasses
from ETL.RDS.rds_df_utils.rds_df_utils import RDSConfigTable
from pipeline_checks.utils.commons import read_repo_json_file, get_lineage_class_exclusions

errors = []
expected_keys = ['target_type', 'target_endpoint', 'src0_type', 'src0_endpoint', 'etl_script_path']
expected_keys_error_str = f"lineage is missing value for one or more of these mandatory fields\n{expected_keys}"


def table_classes_checks():
    class_exclusions = get_lineage_class_exclusions()
    table_classes = [
        table_class for table_class in TableClasses().table_classes if table_class.__class__.__name__ not in class_exclusions
    ]
    for table_class in table_classes:
        try:
            for key in expected_keys:
                assert table_class.data_lineage[key] != ""
        except Exception as e:
            err = {"class_name": table_class.__class__.__name__, "table_name": table_class.table_name, "error": expected_keys_error_str}
            errors.append(err)


def rds_tables_checks():
    # current_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    # git_cmd = ["git", "show", f"{current_commit}:ETL/RDS/rds_df_utils/rds_data_lineage.json"]
    # data_lineage_dict_list = json.loads(subprocess.check_output(git_cmd).decode().strip())
    file_path = "ETL/RDS/rds_df_utils/rds_data_lineage.json"
    data_lineage_dict_list = read_repo_json_file(file_path)
    rds_tables_dict = RDSConfigTable.get_rds_tables_dict()

    rds_table_names = [el["table_name"].lower() for el in rds_tables_dict]
    data_lineage_table_names = [el["target_endpoint"].lower() for el in data_lineage_dict_list]
    for rds_table_name in rds_table_names:
        if rds_table_name not in data_lineage_table_names:
            err = {"class_name": "RDS", "table_name": rds_table_name, "error": "RDS table does not have data_lineage entry"}
            errors.append(err)

    for table_lineage in data_lineage_dict_list:
        try:
            for key in expected_keys:
                assert table_lineage[key] != ""
        except Exception as e:
            err = {"class_name": "RDS sync", "table_name": "", "error": f"error on {table_lineage}\n{expected_keys_error_str}"}
            errors.append(err)


if __name__ == "__main__":
    table_classes_checks()
    rds_tables_checks()
    if errors:
        # print(json.dumps(errors, indent=4))
        raise Exception(json.dumps(errors, indent=4))
    else:
        print("All expected tables have their corresponding data lineage")
