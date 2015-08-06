""" file: config.py (syns)
    author: Jess Robertson

    description: Config file for running Flask app, lifted and lightly modified from 
        Miguel's 'Flask Web Development' book.
"""

import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    """ Base configuration class
    """

    SECRET_KEY = os.environ.get('SECRET_KEY') \
                 or 'something great goes in here'

    # Key for storieswithdata
    SLACK_API_KEY = "8s0OQPVpz1I85Km5rRtNI0ff"

    # Redis stuff
    MEASUREMENT_LIST_KEY_PREFIX = 'measurements'
    MEASUREMENT_LIST_MAX_LENGTH = 100

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    """ Configuration for development environment
    """

    DEBUG = True
    REDIS_URL = "redis://localhost:6379/0"
    USE_UUID_NAMESPACE = False


class TestingConfig(Config):

    """ Configuration for testing
    """

    TESTING = True
    REDIS_URL = "redis://localhost:6379/0"


class ProductionConfig(Config):

    """ Configuration for production
    """

    REDIS_URL = "redis://localhost:6379/0"


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}