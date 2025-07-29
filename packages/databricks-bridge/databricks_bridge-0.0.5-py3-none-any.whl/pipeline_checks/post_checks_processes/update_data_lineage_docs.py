import json
import subprocess
import time
import datetime
import sys

from databricks_execute.utils.auto_schema_update_table_classes import TableClasses
from pipeline_checks.utils.commons import read_repo_json_file, get_lineage_class_exclusions

source_branch = None
data_lineage_branch = "data_lineage_docs_auto_update"


def commit_to_branch():
    # current_branch = source_branch
    print("source_branch = " + str(source_branch))
    cmd_calls = [
        ["git", "add", "."],
        ["git", "status"],
        ["git", "commit", "-m", '"refactor: auto data_lineage docs update from pull_flow ga workflow"'],
        # ["git", "commit", "--amend", "--no-edit"],
        # ["git", "checkout", source_branch],
        # ["git", "rebase", pull_flow_branch],
        # ["git", "push"],
        ["git", "push", "--set-upstream", "origin", data_lineage_branch],
        # ["git", "push", "-f"],
        # ["git", "branch", "-D", pull_flow_branch]
    ]

    if source_branch:
        for cmd in cmd_calls:
            subprocess.run(cmd)
            time.sleep(2)
        subprocess.run(["git", "push", "--set-upstream", "origin", data_lineage_branch])
    # subprocess.run(['echo "branch_updated=$(echo true)" >> $GITHUB_ENV'])


def update_data_lineage_map(lakehouse_dir: str):
    cmd = [
        "python",
        lakehouse_dir + "/docs/ETL/markdown_table_builder.py",
        lakehouse_dir + "/docs/ETL/data_lineage_databricks_to_src.json"
    ]
    lineage_md_table = subprocess.check_output(cmd).decode().strip()
    md_file_path = lakehouse_dir + "/docs/ETL/data_lineage_map.md"
    md_file_data = "# Data Lineage\n\n## Databricks tables to source\n\n" + lineage_md_table
    md_file_data += "\n\nlast updated at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f = open(md_file_path, "w")
    f.write(md_file_data)
    f.close()
    time.sleep(5)


def update_data_lineage_json_file(file_path, expected_data_lineage):
    f = open(file_path, "w")
    f.write(json.dumps(expected_data_lineage, indent=4))
    f.close()
    time.sleep(5)


def update_data_lineage_files():
    class_exclusions = get_lineage_class_exclusions()
    etls_data_lineage_list = [table_class.data_lineage for table_class in TableClasses().table_classes if table_class.__class__.__name__ not in class_exclusions]

    file_path = "ETL/RDS/rds_df_utils/rds_data_lineage.json"
    rds_data_lineage_list = read_repo_json_file(file_path)

    expected_data_lineage = etls_data_lineage_list + rds_data_lineage_list

    file_path = "docs/ETL/data_lineage_databricks_to_src.json"
    actual_data_lineage_list = read_repo_json_file(file_path)

    if expected_data_lineage != actual_data_lineage_list:
        pwd = subprocess.check_output(["pwd"]).decode().strip()
        lakehouse_dir = pwd.split("pipeline_checks")[0]

        if source_branch:
            subprocess.run(["git", "config", "--global", "user.email", '"databricks@y-tree.com"'])
            subprocess.run(["git", "config", "--global", "user.name", '"y-tree"'])
            subprocess.run(["git", "fetch", "origin", source_branch])
            subprocess.run(["git", "checkout", source_branch])
            subprocess.run(["git", "checkout", "-b", data_lineage_branch])

        file_path = lakehouse_dir + "/" + file_path
        update_data_lineage_json_file(file_path, expected_data_lineage)
        update_data_lineage_map(lakehouse_dir)
        commit_to_branch()


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        source_branch = args[1]
    update_data_lineage_files()

# source branch argument is meant for pipeline run. local runs should be triggered without the source branch argument
# python pipeline_checks/post_checks_processes/update_data_lineage_docs.py DT-0000-feat-branch-name
# python pipeline_checks/post_checks_processes/update_data_lineage_docs.py
