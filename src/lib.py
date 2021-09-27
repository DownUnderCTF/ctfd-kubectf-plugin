import time
import jwt
import requests
from CTFd.utils import cache
from urllib.parse import urlparse
from .errors import Error
from .config import TIMEOUT

AUTH_EXPIRY = 120

def generate_jwt(aud, secret, owner_id='0', admin=False):
    m = {
        'owner_id': str(owner_id),
        'aud': aud,
        'exp': int(time.time()) + AUTH_EXPIRY,
        'admin': admin
    }

    return jwt.encode(m, secret, algorithm='HS256')

def error(error: Error):
    return {'error': error.type, 'message': error.message}, error.code

@cache.memoize(timeout=120)
def get_deployment(host, secret, owner_id, admin, challenge):
    aud = urlparse(host).hostname
    auth = generate_jwt(aud, secret, owner_id, admin)
    res = requests.get(
        f'{host}/deployments/{challenge}',
        headers={'authorization': f'Bearer {auth}'},
        timeout=TIMEOUT)
    return res.json(), res.status_code

def create_deployment(host, secret, owner_id, admin, challenge):
    aud = urlparse(host).hostname
    auth = generate_jwt(aud, secret, owner_id, admin)
    res = requests.post(
        f'{host}/deployments/{challenge}',
        json={},
        headers={'authorization': f'Bearer {auth}'},
        timeout=TIMEOUT)
    cache.delete_memoized(get_deployment, host, secret, owner_id, False, challenge)
    cache.delete_memoized(get_deployment, host, secret, owner_id, True, challenge)
    return res.json(), res.status_code
    
def extend_deployment(host, secret, owner_id, admin, challenge):
    aud = urlparse(host).hostname
    auth = generate_jwt(aud, secret, owner_id, admin)
    res = requests.post(
        f'{host}/deployments/{challenge}',
        json={'extend': True},
        headers={'authorization': f'Bearer {auth}'},
        timeout=TIMEOUT)
    cache.delete_memoized(get_deployment, host, secret, owner_id, False, challenge)
    cache.delete_memoized(get_deployment, host, secret, owner_id, True, challenge)
    return res.json(), res.status_code

def terminate_deployment(host, secret, owner_id, admin, challenge):
    aud = urlparse(host).hostname
    auth = generate_jwt(aud, secret, owner_id, admin)
    res = requests.delete(
        f'{host}/deployments/{challenge}',
        headers={'authorization': f'Bearer {auth}'},
        timeout=TIMEOUT)
    cache.delete_memoized(get_deployment, host, secret, owner_id, False, challenge)
    cache.delete_memoized(get_deployment, host, secret, owner_id, True, challenge)
    return res.json(), res.status_code