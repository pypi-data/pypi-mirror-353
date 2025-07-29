import os
import json
from smart_open import smart_open

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google_auth_oauthlib.flow import InstalledAppFlow

base_path = "/dbfs/FileStore" if os.environ.get('ISDATABRICKS', 'local') == "TRUE" else os.path.abspath('')
local_creds_file_path = "/Users/muhammad-saeedfalowo/Documents/drive_api_credentials.json"


def get_token_path(gdrive: bool = False, gads: bool = False, ga4: bool = False):
    all_args = [v for k, v in locals().items() if v]
    filename = ""
    if len(all_args) != 1:
        raise ValueError(f"Only one 'True' argument is required, but got {len(all_args)}.")
    elif gdrive:
        filename = "gdrive_token.json"
    elif gads:
        filename = "gads_token.json"
    elif ga4:
        filename = "ga4apidataretrie_1739871769222_f61604b3f475.json"

    return f"{base_path}/{filename}"


def read_json_file(path) -> dict:
    file_path = path
    f = smart_open(file_path, 'rb')
    _dict = json.load(f)
    return _dict


def get_gcloud_api_creds(env: dict):
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        drive_api_creds_dict = {
            "installed": {
                "client_id": env["dbutils"].secrets.get(scope="google_drive_secrets", key="client_id"),
                "project_id": env["dbutils"].secrets.get(scope="google_drive_secrets", key="project_id"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": env["dbutils"].secrets.get(scope="google_drive_secrets", key="client_secret"),
                "redirect_uris": ["http://localhost"]
            }
        }
    else:
        drive_api_creds_dict = read_json_file(local_creds_file_path)

    return drive_api_creds_dict


def auth(creds_file_dir: str, scopes: list, token_path: str):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    def _get_creds():
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=creds_file_dir,
            scopes=scopes
        )
        creds = flow.run_local_server(port=0)
        return creds
    creds = None
    # The file gdrive_token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                creds = _get_creds()
        else:
            creds = _get_creds()
    # Save the credentials for the next run
    with open(token_path, "w") as token:
        token.write(creds.to_json())

    return creds


def service_account_auth(key_file_path: str):
    creds = service_account.Credentials.from_service_account_file(key_file_path)
    client = BetaAnalyticsDataClient(credentials=creds)
    return client
