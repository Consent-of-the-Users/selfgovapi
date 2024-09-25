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

    def __init__(self, participants=None, **kwargs):
        super().__init__(**kwargs)

        if participants is None or not isinstance(participants, list) or len(participants) < 2:
            raise ValueError("A conversation requires at least two participants.")

        self.participants = []

        # Validate and append users
        print(participants, "participants")
        for uid in participants:
            user = User.load_by_id(uid)
            if not user:
                raise ValueError(f"User with ID {uid} not found")
            self.participants.append(user)

    @classmethod
    def load_by_user_ids(cls, user_ids):
        """
        Load a conversation by user IDs.
        
        The conversation must include exactly all provided user IDs and no others.

        :param user_ids: List of user IDs to match in the conversation.
        :type user_ids: list
        :return: The conversation if found, else None.
        """
        # Start the base query for conversations
        print('in here')
        query = db.session.query(cls).join(cls.participants).group_by(cls.uid)
        print(query)

        # Add a filter for each user_id to ensure the conversation includes them
        for user_id in user_ids:
            query = query.having(db.func.count(User.uid == user_id) > 0)

        # Ensure the conversation contains exactly the same number of participants
        query = query.having(db.func.count(User.uid) == len(user_ids))

        # Return the first matching conversation or None
        return query.first()
