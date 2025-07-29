from typing import Tuple
from ETL.commons.keycloak_service import get_token
from ETL.commons.api_requests import ms_kube_gateway_api_get_request


def get_keycloak_token(env) -> str:
    return get_token(env)["access_token"]


def ms_datalake_connector_decryption(env: dict, s3_key_path: str) -> Tuple[int, str]:
    # api-endpoint
    PARAMS = {"s3KeyPath": s3_key_path, "encrypted": "true"}
    endpoint = "/v1/ms-datalake-connector/file/download"
    status_code, file_content = ms_kube_gateway_api_get_request(env, endpoint, get_keycloak_token(env), PARAMS)

    return status_code, file_content


"""
How to:

from ETL.commons.decrypt_encrypt_data import ms_datalake_connector_decryption
env = locals()
s3_filepath = "landing/quickbooks/profit-loss-monthly/2022/11/00/profit-loss-monthly_2022-12-07_15_19_txt.json"
status_code, file_content = ms_datalake_connector_decryption(env, s3_filepath)

"""
