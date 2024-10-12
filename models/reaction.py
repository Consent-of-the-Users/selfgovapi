from models.base import BaseModel, db
from models.user import User



class Reactions(BaseModel):
    """
    Represents a reaction to a message.
    """
    __tablename__ = "reactions"

    # from_uid is a one to one relationship between a reaction and a user.
    from_uid = db.Column(db.String(36), db.ForeignKey("users.uid"), nullable=False)
    from_user = db.relationship("User", back_populates="reactions_given")

    # chat_uid is a string of 36 characters
    chat_uid = db.Column(db.String(36), nullable=False)

    # type is an enum that has a value of one of the following: [thumbsUp, thumbDown, heart, hate, laugh, wow, thinking]
    type = db.Column(db.Enum("thumbsUp", "thumbsDown", "love", "hate", "laugh", "awe", "curious", name="reaction_types"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize the reaction.
        """
        from_uid, chat_uid, type = kwargs.get("from_uid"), kwargs.get("chat_uid"), kwargs.get("type")

        if not from_uid:
            raise ValueError("From user uid is required")
        
        if not chat_uid:
            raise ValueError("Chat uid is required")
        
        if not type:
            raise ValueError("Type is required")

        self.from_uid = from_uid
        self.chat_uid = chat_uid
        self.type = type

        super(Reaction, self).__init__(**kwargs)

    def __repr__(self):
        """
        Return the reaction type.
        """
        return self.type
