from flask import Blueprint


from routes.client import clients_v1
from routes.user import users_v1
from routes.conversation import conversations_v1

v1 = Blueprint("v1", __name__, url_prefix="/v1")

blueprints = [clients_v1, users_v1, conversations_v1]

for bp in blueprints:
    v1.register_blueprint(bp)

API_VERSIONS = [v1]
