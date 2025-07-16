from app import create_app, register_blueprints
from db import mysql_connection
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
from os import getenv


# load .env variables into the environment
load_dotenv()

# env variable determines if running in production
PRODUCTION = getenv("PRODUCTION")

# Initialize the flask app
app = create_app()

if not PRODUCTION:
    # Enable CORS for all domains
    CORS(app, resources={r"/*": {"origins": "*"}})

# import all models so that they are registered with the db
from models import *

# Initialize the mysql connection
db = mysql_connection(app)

# Initialize the migration engine
migrate = Migrate(app, db)

# Register all the routes in the app
register_blueprints(app)

# Register the before and after request handlers
from before_request import before_request

# from after_requests import after_request

from authorization import authorize_route


@app.route("/status", strict_slashes=False)
@authorize_route
def status():
    return {"message": "OK"}, 200
