from flask import Blueprint

"""
users_v1 = Blueprint("users", __name__, url_prefix="/users")

from routes.user.user import all_users, users_by_id
"""

reactions_v1 = Blueprint("reactions", __name__, url_prefix="/reactions")

from routes.reaction.reaction import reactions_by_chat, reactions_by_chat_user_type
