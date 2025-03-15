from models.convo import Convo
from models.base import db

class GroopConvo(Convo):
    """A groop conversation. 'groop' is a keyword in mysql so I avoid it with 'groop'."""

    title = db.Column(db.String(255))
    groop_uid = db.Column(db.String(36), db.ForeignKey("groops.uid"))
    groop = db.relationship("Groop", back_populates="convos")

    __mapper_args__ = {
        "polymorphic_identity": "groop_convo"
    }

    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.groop = kwargs.get("groop")
        super(GroopConvo, self).__init__(**kwargs)

    def add_participant(self, participant):
        """Allows a single member to be added to a group convo."""
        from models.user import User

        if not isinstance(participant, User):
            raise TypeError("Participant must be a User instance.")
        
        if not participant in self.groop.members:
            raise ValueError(f"User {participant.uid} is not a member of the groop.")
        
        if participant in self.participants:
            raise ValueError(f"User {participant.uid} already exists in the group convo.")

        self.participants.append(participant)
        self.save()
    
    def remove_participant(self, user):
        """Removes a member from the group convo."""
        if not user in self.participants:
            raise ValueError(f"User {user.uid} does not exist in the group convo.")
        
        self.participants.remove(user)
        self.save()
        if len(self.participants) == 0:
            self.delete()
    
