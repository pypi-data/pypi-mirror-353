import keyring
import requests

SERVICE_NAME = "pullapprove_cli"


def save_api_key(*, host, key):
    keyring.set_password(SERVICE_NAME, host, key)


def get_api_key(*, host):
    return keyring.get_password(SERVICE_NAME, host)


def delete_api_key(*, host):
    keyring.delete_password(SERVICE_NAME, host)


def get_requests_session(*, host):
    session = requests.Session()
    session.headers["User-Agent"] = "git-review"
    session.headers["Authorization"] = f"Bearer {get_api_key(host=host)}"
    return session
