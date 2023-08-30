import re
from urllib.parse import urlparse

import requests
from CTFd.plugins import bypass_csrf_protection
from CTFd.utils import get_config, set_config
from CTFd.utils.modes import TEAMS_MODE
from CTFd.utils.decorators import admins_only, ratelimit
from CTFd.utils.logging import log
from CTFd.utils.user import get_current_user
from CTFd.utils.decorators import during_ctf_time_only
from flask import Blueprint, render_template, request

from .config import CHALLENGE_REGEX, CONFIG_HOST, CONFIG_SECRET
from .errors import (ConfigurationError, InvalidRequest, NotAuthenticatedError,
                     UnknownError, ValidationError)
from .lib import error, get_deployment, create_deployment, extend_deployment, terminate_deployment

blueprint = Blueprint(
    'kube_ctf',
    __name__,
    template_folder='templates',
    static_folder='assets')


def register_app(app):
    app.register_blueprint(blueprint)


@blueprint.route('/api/kube_ctf/<challenge>', methods=['GET', 'POST'])
@bypass_csrf_protection
@during_ctf_time_only
@ratelimit(method='GET', limit=15, interval=60, key_type='user', key_prefix='rl_kctfget')
@ratelimit(method='POST', limit=4, interval=60, key_type='user', key_prefix='rl_kctfpost')
def get_challenge(challenge):
    session = get_current_user()

    if not session or not session.id or not session.team_id:
        return error(NotAuthenticatedError)
    
    owner_id = session.id
    if get_config('user_mode') == TEAMS_MODE:
        owner_id = session.team_id


    if not re.match(CHALLENGE_REGEX, challenge):
        return error(ValidationError)
    challenge = challenge.lower()

    host = get_config(CONFIG_HOST)
    secret = get_config(CONFIG_SECRET)
    if not host or not secret:
        return error(ConfigurationError)

    try:
        if request.method == 'GET':
            return get_deployment(host, secret, owner_id, False, challenge)
        elif request.method == 'POST' and request.is_json:
            if request.json.get('action') == 'create':
                return create_deployment(host, secret, owner_id, False, challenge)
            elif request.json.get('action') == 'extend':
                return extend_deployment(host, secret, owner_id, False, challenge)
            elif request.json.get('action') == 'terminate':
                return terminate_deployment(host, secret, owner_id, False, challenge)
            else:
                return error(InvalidRequest)
        else:
            return error(InvalidRequest)
    except Exception as e:
        log('kube_ctf', 'unknown error: {error}', error=e)
        return error(UnknownError)


@blueprint.route('/admin/kube_ctf', methods=['GET', 'POST'])
@admins_only
def get_config_page():
    alert = None
    if request.method == 'POST':
        host = request.form.get('host', '')
        secret = request.form.get('secret', '')
        if not isinstance(host, str) or not isinstance(secret, str):
            alert = {'type': 'danger', 'message': 'Invalid config.'}
        else:
            alert = {
                'type': 'success',
                'message': 'Configuration successfully saved!'
            }
            set_config(CONFIG_HOST, host)
            set_config(CONFIG_SECRET, secret)

    return render_template(
        'admin.html',
        host=get_config(CONFIG_HOST, ''),
        secret=get_config(CONFIG_SECRET, ''),
        alert=alert)
