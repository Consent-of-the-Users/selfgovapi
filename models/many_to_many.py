from db import db


users_conversations = db.Table(
    'users_conversations',
    db.Column('user_uid', db.String(36), db.ForeignKey('users.uid'), primary_key=True),
    db.Column('conversation_uid', db.String(36), db.ForeignKey('conversation.uid'), primary_key=True)
)