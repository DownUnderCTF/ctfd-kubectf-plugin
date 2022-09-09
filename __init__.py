from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES

from .events import *
from .kube_challenge import KubeChallengeType, PLUGIN_FOLDER_NAME
from .routes import register_app

# Global dictionary used to hold all the Challenge Type classes used by CTFd.
# Insert into this dictionary to register your Challenge Type.
CHALLENGE_CLASSES["kubectf"] = KubeChallengeType


def load(app):
    register_plugin_assets_directory(app,
                                     base_path=f"/plugins/{PLUGIN_FOLDER_NAME}/assets/")

    app.db.create_all()
    register_app(app)