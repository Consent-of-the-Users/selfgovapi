from models.base import BaseModel, db
from models.many_to_many import users_convos, users_groops

class User(BaseModel):
    """
    Users of the app, associated with a given client.
    """
    __tablename__ = "users"

    name = db.Column(db.String(36), nullable=False)
    handle = db.Column(db.String(36), nullable=False, unique=True)
    email = db.Column(db.String(36), nullable=False)

    # TODO: reevaluate convos into groups

    # Many-to-many relationship with convos via the user_convos table
    convos = db.relationship("Convo", secondary=users_convos, back_populates="participants")
    
    # Many-to-many relationship with groops via the user_groops table
    groops = db.relationship("Groop", secondary=users_groops, back_populates="members")


    def __init__(self, **kwargs):

        name, handle = kwargs.get("name"), kwargs.get("handle")
        email, uid = kwargs.get("email"), kwargs.get("uid")

        if not name:
            raise ValueError("User name is required")
        
        if not handle:
            raise ValueError("User handle is required")
        
        if not email:
            raise ValueError("User email is required")
        
        if not uid:
            raise ValueError("User uid is required")

        self.uid = kwargs.get("uid")
        self.name = kwargs.get("name")
        self.handle = kwargs.get("handle")
        self.email = kwargs.get("email")


        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return self.name