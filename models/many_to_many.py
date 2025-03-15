from db import db


users_convos = db.Table(
    'users_convos',
    db.Column('user_uid', db.String(36), db.ForeignKey('users.uid'), primary_key=True),
    db.Column('convo_uid', db.String(36), db.ForeignKey('convos.uid'), primary_key=True)
)

users_groops = db.Table(
    'users_groops',
    db.Column('user_uid', db.String(36), db.ForeignKey('users.uid'), primary_key=True),
    db.Column('groop_uid', db.String(36), db.ForeignKey('groops.uid'), primary_key=True)
)
