from flask import Blueprint

groops_v1 = Blueprint("groops", __name__, url_prefix="/groops")

from routes.groop.groop import all_groops
