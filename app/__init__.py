""" file:   __init__.py (hermes.api)
    author: Jess Robertson
"""

from uuid import uuid1 as uuid

from flask import Flask, Blueprint
from flask.ext.restful import Api, Resource, url_for

from .config import config
from .bot import BotAPI


def create_app(config_name):
    """ Create an application with the given configuration
    """
    # Configure application
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Register API blueprints
    api_blueprint = Blueprint('api', __name__)
    api = Api(api_blueprint)

    # Resources
    api.add_resource(BotAPI, '/')
    app.register_blueprint(api_blueprint)

    return app
 
