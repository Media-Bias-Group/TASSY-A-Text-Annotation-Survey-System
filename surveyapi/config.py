"""
config.py
- settings for the flask application object
"""

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="unisurveyapp",
    password="ZBMTzdzCMmb4@vv",
    hostname="unisurveyapp.mysql.pythonanywhere-services.com",
    databasename="unisurveyapp$production_00"
)

class BaseConfig(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 299
    SECRET_KEY = 'kanishkunipassau'