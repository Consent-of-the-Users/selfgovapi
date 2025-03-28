from db import db, firebase_connection

firestore = firebase_connection()

def serialize_obj_lists_for_firestore(obj):
    """
    ORM objects need a Firestore-friendly dictionary with lists of UIDs.
    """
    obj_dict = obj.to_dict()
    
    # ignore private attributes
    for attr_name in dir(obj):
        if attr_name.startswith("_"):
            continue

        attr_value = getattr(obj, attr_name, None)

        # if it's a list of objects with UIDs, replace with a list of UIDs
        if isinstance(attr_value, list) and attr_value and hasattr(attr_value[0], "uid"):
            obj_dict[attr_name] = [item.uid for item in attr_value]  # Convert to list of UIDs
    
    return obj_dict


def save_to_firestore(obj):
    """
    Save an object to Firestore
    """
    # normalize class names to firestore's standard
    class_name = obj.__class__.__name__.lower()

    table_name = class_name + "s"

    # associate class name with the firestore collection
    doc_ref = firestore.collection(table_name).document(obj.uid)
    
    # Get the document snapshot to check existence and print its data
    doc_snapshot = doc_ref.get()

    # firestore is nosql, so it needs a dedicated list of ID strings for quick reads related to membership
    obj_dict = serialize_obj_lists_for_firestore(obj)

    # Create the document or update it if it already exists.
    if not doc_snapshot.exists:
        doc_ref.set(obj_dict)
    else:
        doc_ref.update(obj_dict)


def delete_from_firestore(obj):
    """
    Delete an object from Firestore
    """

    # normalize class names
    class_name = obj.__class__.__name__.lower()

    table_name = class_name + "s"

    # delete document by uid
    firestore.collection(table_name).document(obj.uid).delete()

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
        from datetime import datetime

        old_updated_at = self.updated_at
        try:
            self.updated_at = datetime.now()
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            self.updated_at = old_updated_at
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
    def load_by_uid(cls, uid):
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
        '''
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }'
        '''
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if hasattr(self, column.name)
        }