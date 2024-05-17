from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_restful import Api
import os

# Load environment variables from .env file
load_dotenv()

# Instantiate app
app = Flask(__name__)

# Set a secret key (needed for browser cookies)
app.secret_key = os.environ['SECRET_KEY']

# Set SQLAlchemy configurations
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Define naming convention
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
# Define metadata, instantiate db
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)

# Instantiate Migrate
migrate = Migrate(app, db)

# Instantiate Bcrypt
bcrypt = Bcrypt(app)

app.json.compact = False

# Instantiate REST API
api = Api(app)
