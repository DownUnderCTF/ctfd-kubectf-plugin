import math
from os import path

from CTFd.models import Challenges, Solves, db
from CTFd.plugins.dynamic_challenges import DynamicValueChallenge
from CTFd.utils.modes import get_model
from CTFd.plugins.dynamic_challenges.decay import DECAY_FUNCTIONS, logarithmic

from .routes import blueprint

PLUGIN_FOLDER_NAME = path.basename(path.dirname(__file__))


class KubeChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "kubectf"}
    id = db.Column(db.Integer,
                   db.ForeignKey("challenges.id", ondelete="CASCADE"),
                   primary_key=True)
    template_name = db.Column(db.String(255), index=False, default="")

    initial = db.Column(db.Integer, default=0)
    minimum = db.Column(db.Integer, default=0)
    decay = db.Column(db.Integer, default=0)
    function = db.Column(db.String(32), default="logarithmic_custom")

    def __init__(self, *args, **kwargs):
        super(KubeChallenge, self).__init__(**kwargs)
        self.template_name = kwargs["template_name"]
        self.value = kwargs["initial"]


class KubeChallengeType(DynamicValueChallenge):
    id = "kubectf"  # Unique identifier used to register challenges
    name = "kubectf"  # Name of a challenge type
    templates = {  # Templates used for each aspect of challenge editing & viewing
        "create": f"/plugins/{PLUGIN_FOLDER_NAME}/templates/create.html",
        "update": f"/plugins/{PLUGIN_FOLDER_NAME}/templates/update.html",
        "view": f"/plugins/{PLUGIN_FOLDER_NAME}/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": f"/plugins/{PLUGIN_FOLDER_NAME}/assets/create.js",
        "update": f"/plugins/{PLUGIN_FOLDER_NAME}/assets/update.js",
        "view": f"/plugins/{PLUGIN_FOLDER_NAME}/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = f"/plugins/{PLUGIN_FOLDER_NAME}/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = blueprint
    challenge_model = KubeChallenge


    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.
        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = KubeChallenge.query.filter_by(id=challenge.id).first()

        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "initial": challenge.initial,
            "decay": challenge.decay,
            "minimum": challenge.minimum,
            "template_name": challenge.template_name,
            "description": challenge.description,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            },
        }
        return data

    @classmethod
    def update(cls, challenge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.
        :param challenge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()

        for attr, value in data.items():
            # We need to set these to floats so that the next operations don't operate on strings
            if attr in ("initial", "minimum", "decay"):
                value = float(value)
            setattr(challenge, attr, value)

        return KubeChallengeType.calculate_value(challenge)

    @classmethod
    def solve(cls, user, team, challenge, request):
        super().solve(user, team, challenge, request)

        KubeChallengeType.calculate_value(challenge)