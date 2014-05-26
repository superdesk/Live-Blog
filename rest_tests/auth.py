from requests import Session
from urllib.parse import urljoin
import hashlib
import hmac
import json

from settings import SERVER_URL, ADMIN_LOGIN, ADMIN_PASS

SERVER_URL = SERVER_URL.rstrip('/')


class ApiAuthException(Exception):
    pass


def hash_token(username, password, token):
    sha_password = hashlib.sha512(password.encode()).hexdigest()
    hashed_username = hmac.new(
        username.encode(),
        sha_password.encode(),
        hashlib.sha512
    ).hexdigest()
    hashed_token = hmac.new(
        bytes(hashed_username.encode()),
        bytes(token.encode()),
        hashlib.sha512
    ).hexdigest()
    return hashed_token


def get_token(username=ADMIN_LOGIN, password=ADMIN_PASS, session=None):
    if session is None:
        session = Session()

    # step1_url = urljoin(SERVER_URL, '/resources/Security/Authentication')
    step1_url = SERVER_URL + '/Security/Authentication'
    step1 = session.post(
        url=step1_url,
        data={
            'userName': username,
        },
        verify=False
    )
    try:
        step1_answer = json.loads(step1.text)
    except ValueError as e:
        raise ApiAuthException(step1_url, step1.text, e)
    try:
        token = step1_answer['Token']
    except KeyError as e:
        raise ApiAuthException(step1_url, step1.text, e)

    hashed_token = hash_token(username, password, token)

    # step2_url = urljoin(SERVER_URL, '/resources/Security/Authentication/Login')
    step2_url = SERVER_URL + '/Security/Authentication/Login'
    step2 = session.post(
        url=step2_url,
        data={
            'UserName': username,
            'Token': token,
            'HashedToken': hashed_token
        },
        verify=False
    )
    try:
        step2_answer = json.loads(step2.text)
    except ValueError as e:
        raise ApiAuthException(step2_url, step2.text, e)
    try:
        session_key = step2_answer['Session']
    except KeyError as e:
        raise ApiAuthException(step2_url, step2.text, e)
    return session_key
