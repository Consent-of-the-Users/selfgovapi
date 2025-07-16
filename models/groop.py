from models.base import BaseModel, db
from models.many_to_many import users_groops
from models.user import User
from models.master_groop_convo import MasterGroopConvo


class Groop(BaseModel):
    """Group of users."""

    __tablename__ = "groops"

    name = db.Column(db.String(255), nullable=False, unique=True)
    handle = db.Column(db.String(36), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    members = db.relationship("User", secondary=users_groops, back_populates="groops")

    convos = db.relationship(
        "GroopConvo", back_populates="groop", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        name, handle = kwargs.get("name"), kwargs.get("handle")
        description = kwargs.get("description")
        members = kwargs.get("members")

        if not (name and handle and description and members):
            raise ValueError("Groop requires name, handle, description, and members.")

        if not isinstance(members, list) and isinstance(members[0], User):
            raise TypeError("Members must be a list of Users.")

        self.name = name
        self.handle = handle
        self.description = description
        self.members.extend(members)

        super(Groop, self).__init__(**kwargs)

    @property
    def master_convo(self):
        """Retrieve the group's master conversation, or create one if missing."""

        mc = db.session.query(MasterGroopConvo).filter_by(groop_uid=self.uid).first()

        if not mc:
            title = f"Master Convo for @{self.handle}."
            groop = self
            data = {"title": title, "groop": groop}
            mc = MasterGroopConvo(**data)
            mc.save()

        return mc

    def add_member(self, user):
        """Adds a new member to the groop."""
        from models.user import User

        if not isinstance(user, User):
            raise TypeError("Members must be users.")

        if user in self.members:
            raise ValueError(f"User {user.uid} is already a member of the groop.")

        self.members.append(user)
        self.save()

    def remove_member(self, user):
        """Removes a member from the groop. Deletes groop if they were the last member."""
        from models.user import User

        if not isinstance(user, User):
            raise TypeError("Members must be users.")

        if not user in self.members:
            raise ValueError(f"User {user.uid} is not a member of the groop.")

        self.members.remove(user)
        self.save()

        if len(self.members) == 0:
            self.delete()
