"""
config.py
- settings for the flask application object
"""

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="user",
    password="pass",
    hostname="hostm",
    databasename="db"
)

class BaseConfig(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 299
    SECRET_KEY = 'key'
