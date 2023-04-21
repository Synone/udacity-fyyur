import os

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:03031998@localhost:5432/fyyur"  # replace this URI by your database URI
SQLALCHEMY_TRACK_MODIFICATIONS = True
