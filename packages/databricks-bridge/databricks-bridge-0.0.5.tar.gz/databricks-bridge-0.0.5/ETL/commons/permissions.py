from pyspark.sql import SparkSession


groups_dict = {
    "admin": "admin",
    "analysts": "analysts",
    "finance": "finance",
    "ifls": "ifls",
    "data_engineer_london": "data_engineer_london",
}


def schema_permissions(schema_name: str, groups: list):
    base_grants = [
        f"GRANT USAGE ON SCHEMA {schema_name} TO <group>;",
        f"GRANT SELECT ON SCHEMA {schema_name} TO <group>;",
        f"GRANT READ_METADATA ON SCHEMA {schema_name} TO <group>;",
    ]

    return [grant_sql.replace("<group>", groups_dict[group_el]) for grant_sql in base_grants for group_el in groups]


def grant_permissions(spark: SparkSession, db_name: str, groups: list):
    for grant_sql in schema_permissions(db_name, groups):
        spark.sql(grant_sql)
