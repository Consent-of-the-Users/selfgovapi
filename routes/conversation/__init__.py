from flask import Blueprint

conversations_v1 = Blueprint("conversations", __name__, url_prefix="/conversations")

from routes.conversation.conversation import conversation_by_user_ids, remove_participant