from models.base import BaseModel, db
from models.many_to_many import users_convos
from models.user import User

class Convo(BaseModel):
    """Base class for all convos (DMs & Groups)."""
    __tablename__ = "convos"

    _latest_msg = db.Column(db.String(36), nullable=True)
    _latest_msg_uid = db.Column(db.String(36), nullable=True)
    type = db.Column(db.String(24))

    participants = db.relationship("User", secondary=users_convos, back_populates="convos")

    __mapper_args__ = {
        "polymorphic_identity": "convo",
        "polymorphic_on": type
    }

    def __init__(self, **kwargs):
        self.latest_msg = None
        self.latest_msg_uid = None
        self.title = None
        self.groop_uid = None
        self.groop = None
        super(Convo, self).__init__(**kwargs)

    @property
    def latest_msg(self):
        """The latest message in the convo."""
        return self._latest_msg

    @latest_msg.setter
    def latest_msg(self, msg):
        """Update the latest message and its UID."""
        self._latest_msg = msg
        #self._latest_msg_uid = msg.uid
        self._latest_msg_uid = 0
    
    def add_participant(self, participant):
        """There must be exactly two Convo participants."""
        from models.user import User

        if self.participants and len(self.participants) == 2:
            raise ValueError("There can only be two participants in a DM Convo.")

        if not isinstance(participant, User):
            raise TypeError("Participant must be a User.")
    
        self.participants.append(participant)

'''
    @classmethod
    def load_by_user_ids_and_is_group(cls, user_ids):
        """
        Load a convo by user IDs and is_group boolean.
        
        The convo must include exactly all provided user IDs and no others,
        and match the provided is_group value.

        :param user_ids: List of user IDs to match in the convo.
        :type user_ids: list
        :param is_group: Boolean value indicating if the convo is a group.
        :type is_group: bool
        :return: The convo if found, else None.
        """
        # Ensure we are working with a set of user_ids for comparison
        user_ids_set = set(user_ids)

        # Query convos that match is_group and have the correct number of participants
        convos = (
            db.session.query(cls)
            .join(cls.participants)
            .group_by(cls.uid)
            .having(db.func.count(User.uid.distinct()) == len(user_ids_set))  # Ensures correct number of distinct users
            .all()
        )

        # Filter out any convos that don't match exactly all user_ids
        for convo in convos:
            convo_user_ids = set([user.uid for user in convo.participants])
            if convo_user_ids == user_ids_set:
                return convo

        return None
'''