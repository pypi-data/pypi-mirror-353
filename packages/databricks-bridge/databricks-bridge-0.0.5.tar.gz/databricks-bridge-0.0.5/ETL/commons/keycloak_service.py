from typing import Dict
import base64

from keycloak import KeycloakOpenID
from smart_open import smart_open
import json
import os


def read_keycloak_creds_from_local() -> dict:
    file_path = "<base_path>/keycloak_credentials.json"
    f = smart_open(file_path, 'rb')
    keycloak_creds_dict = json.load(f)
    return keycloak_creds_dict["uat"]


def get_keycloak_creds(env: dict):
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        keycloak_creds_dict = {
            "KEYCLOAK_SERVER_URL": env["dbutils"].secrets.get(scope="keycloak_secrets", key="keycloak_server_url"),
            "KEYCLOAK_CLIENT_ID": env["dbutils"].secrets.get(scope="keycloak_secrets", key="keycloak_client_id"),
            "KEYCLOAK_CLIENT_SECRET_KEY": env["dbutils"].secrets.get(scope="keycloak_secrets", key="keycloack_client_secret_key")
        }
    else:
        keycloak_creds_dict = read_keycloak_creds_from_local()

    return keycloak_creds_dict


def get_open_id(env: dict) -> KeycloakOpenID:
    keycloak_attr = get_keycloak_creds(env)
    return KeycloakOpenID(
        server_url=base64.b64decode(keycloak_attr['KEYCLOAK_SERVER_URL']).decode("utf-8"),
        client_id=base64.b64decode(keycloak_attr['KEYCLOAK_CLIENT_ID']).decode("utf-8"),
        realm_name="service",
        client_secret_key=base64.b64decode(keycloak_attr['KEYCLOAK_CLIENT_SECRET_KEY']).decode("utf-8")
    )


def get_token(env) -> Dict:
    return get_open_id(env).token(grant_type=["client_credentials"])
