from models.base import BaseModel, db
from models.many_to_many import users_conversations
from models.user import User

class Conversation(BaseModel):
    """
    Represents a conversation between two or more users and/or groups.
    """
    __tablename__ = "conversations"

    # Many-to-many relationship with users via the user_conversations table
    participants = db.relationship("User", secondary=users_conversations, back_populates="conversations")
    # bolean for is_group
    is_group = db.Column(db.Boolean, default=False)
    title = db.Column(db.String(255), nullable=True)

    def __init__(self, **kwargs):
        is_group = kwargs.get('is_group')
        title = kwargs.get('title')
        self.is_group = is_group
        self.title = title
        super().__init__(**kwargs)

    @classmethod
    def load_by_user_ids_and_is_group(cls, user_ids, is_group):
        """
        Load a conversation by user IDs and is_group boolean.
        
        The conversation must include exactly all provided user IDs and no others,
        and match the provided is_group value.

        :param user_ids: List of user IDs to match in the conversation.
        :type user_ids: list
        :param is_group: Boolean value indicating if the conversation is a group.
        :type is_group: bool
        :return: The conversation if found, else None.
        """
        # Ensure we are working with a set of user_ids for comparison
        user_ids_set = set(user_ids)

        # Query conversations that match is_group and have the correct number of participants
        conversations = (
            db.session.query(cls)
            .join(cls.participants)
            .filter(cls.is_group == is_group)  # Ensure is_group matches
            .group_by(cls.uid)
            .having(db.func.count(User.uid.distinct()) == len(user_ids_set))  # Ensures correct number of distinct users
            .all()
        )

        # Filter out any conversations that don't match exactly all user_ids
        for conversation in conversations:
            conversation_user_ids = set([user.uid for user in conversation.participants])
            if conversation_user_ids == user_ids_set:
                return conversation

        return None
