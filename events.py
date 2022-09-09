from urllib.parse import urlparse

import requests
from CTFd.models import Challenges, Solves, Teams, db
from CTFd.utils import get_config
from CTFd.utils.logging import log
from CTFd.utils.user import get_current_user
from sqlalchemy import event

from .config import CONFIG_HOST, CONFIG_SECRET, TIMEOUT
from .lib import generate_jwt


