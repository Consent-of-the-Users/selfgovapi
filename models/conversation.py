from models.base import BaseModel, db
from models.many_to_many import users_conversations
from models.user import User

class Conversations(BaseModel):
    """
    Represents a conversation between two or more users and/or groups.
    """
    __tablename__ = "conversations"

    # Many-to-many relationship with users via the user_conversations table
    participants = db.relationship("User", secondary=users_conversations, back_populates="conversations")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def load_by_user_ids(cls, user_ids):
        """
        Load a conversation by user IDs.
        
        The conversation must include exactly all provided user IDs and no others.

        :param user_ids: List of user IDs to match in the conversation.
        :type user_ids: list
        :return: The conversation if found, else None.
        """
        # Ensure we are working with a set of user_ids for comparison
        user_ids_set = set(user_ids)

        # Query all conversations and filter by participant user IDs
        conversations = db.session.query(cls).join(cls.participants).group_by(cls.uid).having(
            db.func.count(User.uid.distinct()) == len(user_ids_set)  # Ensures correct number of distinct users
        ).all()

        # Filter out any conversations that don't match exactly all user_ids
        for conversation in conversations:
            conversation_user_ids = set([user.uid for user in conversation.participants])
            if conversation_user_ids == user_ids_set:
                return conversation

        return None

