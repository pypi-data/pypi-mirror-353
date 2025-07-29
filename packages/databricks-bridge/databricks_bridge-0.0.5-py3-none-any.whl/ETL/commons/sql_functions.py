

def mask_pii_func(allowed_group: str = "pii_users"):
    fcn_name = "mask_pii"
    sql_cmd = f"""
        CREATE OR REPLACE FUNCTION mask_pii(pii_col STRING) RETURN
        CASE WHEN is_member('{allowed_group}') THEN pii_col ELSE 'REDACTED' END;
    """
    return fcn_name, sql_cmd
