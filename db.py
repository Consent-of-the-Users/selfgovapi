from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from os import getenv


# initialize the db object
db = SQLAlchemy()

# load .env variables into the environment
load_dotenv()

# get database credentials from environment variables
db_name = getenv("DB_NAME")
db_user = getenv("DB_USER")
db_password = getenv("DB_PASSWORD")
db_host = getenv("DB_HOST")
db_port = getenv("DB_PORT")
firestore_path = getenv("FIRESTORE_PATH")

if not (db_name and db_user and db_password and db_host and db_port):
    raise ValueError("Database credentials are not set. Please set them in a .env file")


def mysql_connection(app):
    """
    Initialize the mysql connection
    Return: db object
    """

    # create the connection uri
    uri = "mysql+pymysql://{}:{}@{}:{}/{}".format(
        db_user, db_password, db_host, db_port, db_name
    )

    # update the app configuration with the connection uri
    # disabling the modification tracker until flask-migrate is setup
    app.config.update(
        SQLALCHEMY_DATABASE_URI=uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # initialize the db with the app
    db.init_app(app)

    # create tables for all the models
    with app.app_context():
        db.create_all()

    return db


def firebase_connection():
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore

    cred = credentials.Certificate(firestore_path)
    firebase = firebase_admin.initialize_app(cred)

    return firestore.client()
