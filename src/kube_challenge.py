import math

from CTFd.models import Challenges, Solves, db
from CTFd.plugins.challenges import BaseChallenge
from CTFd.utils.modes import get_model

from .routes import blueprint


class KubeChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "kubectf"}
    id = db.Column(db.Integer,
                   db.ForeignKey("challenges.id", ondelete="CASCADE"),
                   primary_key=True)
    template_name = db.Column(db.String(255), index=False, default="")

    initial = db.Column(db.Integer, default=0)
    minimum = db.Column(db.Integer, default=0)
    decay = db.Column(db.Integer, default=0)

    def __init__(self, *args, **kwargs):
        super(KubeChallenge, self).__init__(**kwargs)
        self.template_name = kwargs["template_name"]
        self.initial = kwargs["value"]


class KubeChallengeType(BaseChallenge):
    id = "kubectf"  # Unique identifier used to register challenges
    name = "kubectf"  # Name of a challenge type
    templates = {  # Templates used for each aspect of challenge editing & viewing
        "create": "/plugins/kube_ctf/templates/create.html",
        "update": "/plugins/kube_ctf/templates/update.html",
        "view": "/plugins/kube_ctf/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/kube_ctf/assets/create.js",
        "update": "/plugins/kube_ctf/assets/update.js",
        "view": "/plugins/kube_ctf/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/kube_ctf/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = blueprint
    challenge_model = KubeChallenge

    #  Taken from the Dynamic scoring challenge
    @classmethod
    def calculate_value(cls, challenge):
        Model = get_model()

        solve_count = (Solves.query.join(
            Model, Solves.account_id == Model.id).filter(
                Solves.challenge_id == challenge.id,
                Model.hidden == False,
                Model.banned == False,
            ).count())

        # If the solve count is 0 we shouldn't manipulate the solve count to
        # let the math update back to normal
        if solve_count != 0:
            # We subtract -1 to allow the first solver to get max point value
            solve_count -= 1

        # It is important that this calculation takes into account floats.
        # Hence this file uses from __future__ import division
        value = (((challenge.minimum - challenge.initial) /
                  (challenge.decay**2)) * (solve_count**2)) + challenge.initial

        value = math.ceil(value)

        if value < challenge.minimum:
            value = challenge.minimum

        challenge.value = value
        db.session.commit()
        return challenge

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