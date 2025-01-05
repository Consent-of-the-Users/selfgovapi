from db import db, firebase_connection

firestore = firebase_connection()


def save_to_firestore(obj):
    """
    Save an object to Firestore
    """
    class_name = obj.__class__.__name__.lower()
    if class_name == "user":
        class_name = "users"
    doc_ref = firestore.collection(class_name).document(obj.uid)
    
    # Get the document snapshot to check existence and print its data
    doc_snapshot = doc_ref.get()

    obj_dict = obj.to_dict()

    if class_name == 'conversations':
        x = obj.participants
        obj.user_ids = [user.uid for user in obj.participants]
        obj_dict['participants'] = obj.user_ids

    if doc_snapshot.exists:
        doc_ref.update(obj_dict)
    else:
        doc_ref.set(obj_dict)


def delete_from_firestore(obj):
    """
    Delete an object from Firestore
    """
    class_name = obj.__class__.__name__.lower()
    if class_name == "user":
        class_name = "users"    
    firestore.collection(class_name).document(obj.uid).delete()

# TEST THESE WITH A SCRIPT


class BaseModel(db.Model):
    """
    Base model for serialization/deserialization and shared methods
    """

    __abstract__ = True

    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    uid = db.Column(db.String(36), primary_key=True, nullable=False)

    def __init__(self, **kwargs):
        from uuid import uuid4
        from datetime import datetime

        for key, value in kwargs.items():
            setattr(self, key, value)

        if "uid" not in kwargs:
            self.uid = str(uuid4())

        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self, firestore=True):
        """
        Save to the database
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        if firestore:
            save_to_firestore(self)

        

    def delete(self, firestore=True):
        """
        Delete from the database
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        if firestore:
            delete_from_firestore(self)

    @classmethod
    def load_all(cls):
        """
        Load all the objects from the database
        """
        return db.session.query(cls).all()

    @classmethod
    def load_all_dict(cls, remove_attr=None):
        """
        Load all the objects from the database. Optionally remove an attribute from the response.
        """
        return [
        {k: v for k, v in obj.to_dict().items() if k != remove_attr} 
        for obj in cls.load_all()
        ]

    @classmethod
    def load_by_id(cls, uid):
        """
        Load an object by its uid
        """
        return db.session.get(cls, uid)

    @classmethod
    def load_by_attr(cls, attr, value):
        """
        Load an object by an attribute and its value
        """
        return db.session.query(cls).filter(getattr(cls, attr) == value).first()

    def to_dict(self):
        """
        Serialize the object
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
