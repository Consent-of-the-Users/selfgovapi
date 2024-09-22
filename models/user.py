from models.base import BaseModel, db
from models.client import Client

class User(BaseModel):
    """
    Users of the app, associated with a given client.
    """
    __tablename__ = "users"

    name = db.Column(db.String(36), nullable=False)
    handle = db.Column(db.String(36), nullable=False, unique=True)
    email = db.Column(db.String(36), nullable=False)

    def __init__(self, **kwargs):
        if not kwargs.get("name"):
            raise ValueError("User name is required")
        
        if not kwargs.get("handle"):
            raise ValueError("User handle is required")
        
        if not kwargs.get("email"):
            return ValueError("User email is required")

        self.name = kwargs.get("name")
        self.handle = kwargs.get("handle")
        self.email = kwargs.get("email")

        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return self.name