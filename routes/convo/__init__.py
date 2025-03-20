from flask import Blueprint

convos_v1 = Blueprint("convos", __name__, url_prefix="/convos")

from routes.convo.convo import all_convos, get_convo_by_participants