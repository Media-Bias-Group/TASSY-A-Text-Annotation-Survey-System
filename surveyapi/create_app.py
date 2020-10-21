"""
create_app.py
- creates a Flask app instance and registers the database object
"""
from flask import Flask
from surveyapi.api import api
from surveyapi.config import BaseConfig


def create_app():
    app = Flask(__name__, static_folder="../dist/static", template_folder="../dist")
    app.config.from_object(BaseConfig)
    app.register_blueprint(api, url_prefix="/api")
    return app
