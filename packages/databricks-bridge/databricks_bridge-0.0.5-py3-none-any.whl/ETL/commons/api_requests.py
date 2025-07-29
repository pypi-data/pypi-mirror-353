import os
import time

import requests
from typing import Tuple


def get_ms_kube_gateway_url(env):
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        url = env["dbutils"].secrets.get(scope="ms_kube_gateway_secrets", key="ms_kube_gateway_url")
    else:
        url = "https://ms-kubebricks-gateway.internal.preprod.y-tree.org.uk"
    return url


def get_survicate_api_key(env):
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        api_key = env["dbutils"].secrets.get(scope="survicate_secrets", key="survicate_api_key")
    else:
        api_key = ""
    return api_key


def get_mixpanel_creds(env):
    if os.environ.get('ISDATABRICKS', 'local') == "TRUE":
        username = env["dbutils"].secrets.get(scope="mixpanel_secrets", key="service_account_username")
        secret = env["dbutils"].secrets.get(scope="mixpanel_secrets", key="service_account_secret")
    else:
        username = ""
        secret = ""
    return username, secret


def ms_kube_gateway_api_get_request(env: dict, endpoint, keycloak_token, PARAMS: dict=None) -> Tuple[int, str]:
    # api-endpoint
    """
    expected endpoint format: /v1/ms-life-strategy/life-strategy/*/*
    """
    URL = f"{get_ms_kube_gateway_url(env)}{endpoint}"
    HEADERS = {
        "Authorization": f"Bearer {keycloak_token}"
    }
    # sending get request and saving the response as response object
    res = requests.get(url=URL, params=PARAMS, headers=HEADERS)

    return res.status_code, res.text


def survicate_api_get_request(env: dict, endpoint, PARAMS: dict=None) -> Tuple[int, str]:
    # api-endpoint
    """
    expected endpoint format: /surveys || /surveys/{survey_id}/responses
    """

    api_key = get_survicate_api_key(env)

    URL = f"https://data-api.survicate.com/v2{endpoint}"
    HEADERS = {
        "Authorization": f"Basic {api_key}"
    }
    # sending get request and saving the response as response object
    res = requests.get(url=URL, params=PARAMS, headers=HEADERS)

    return res.status_code, res.text


def api_get_request_timeout(url: str, headers: dict, params: dict = {}, timeout_sec: int = 60, retries_limit: int = 3):
    for i in range(retries_limit):
        try:
            # sending get request and saving the response as response object
            res = requests.get(url=url, params=params, headers=headers, timeout=timeout_sec)
            break
        except requests.exceptions.Timeout:
            print(f"Request timedout after {timeout_sec} seconds")
            if i+1 >= retries_limit:
                return 408, f"Retried {retries_limit} times. Request timedout after {timeout_sec} seconds"

            time.sleep(5)

    return res.status_code, res.text


def mixpanel_api_service_acc_request(env: dict) -> Tuple[int, str]:
    # api-endpoint
    """
    expected endpoint format:

    username: service account username
    secret: service account secret
    """

    username, secret = get_mixpanel_creds(env)

    URL = f"https://mixpanel.com/api/app/me"
    HEADERS = {
        "Authorization": f"Basic {username}:{secret}"
    }
    status_code, text = api_get_request_timeout(url=URL, headers=HEADERS)

    return status_code, text


def mixpanel_api_event_export_request(env: dict, PARAMS: dict) -> Tuple[int, str]:
    # api-endpoint
    """
    expected endpoint format: /export?project_id=123&from_date=yyyy-mm-dd&to_date=yyyy-mm-dd&limit=1
    f"https://data.mixpanel.com/api/2.0/export?project_id=2267320&from_date=2024-05-01&to_date=2024-05-02&limit=1"

    expected PARAMS: {"project_id": 2267320, "from_date": "2024-05-01", "to_date": "2024-05-13", "limit": 10}

    username: service account username
    secret: service account secret
    """

    username, secret = get_mixpanel_creds(env)

    URL = f"https://data.mixpanel.com/api/2.0/export"
    HEADERS = {
        "Authorization": f"Basic {username}:{secret}"
    }
    # sending get request and saving the response as response object
    status_code, text = api_get_request_timeout(url=URL, params=PARAMS, headers=HEADERS)

    return status_code, text


def api_get_request(url: str, headers: dict = {}, params: dict = {}, sleep_secs: float = None):
    ret = requests.get(url=url, headers=headers, params=params)
    if sleep_secs:
        time.sleep(sleep_secs)

    return ret
