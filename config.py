from flask import jsonify, Flask
#from werkzeug import exceptions as ex
# from override_flask import NewFlask as Flask
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
import jinja2
import os
import mongoengine

"""
This file holds configuration variables for the csd. these variables are used
throughout the code, but are stored here to make changing configuration
easier.
"""

# get current working directory (top level of the csd server folder)
BACKUP_DIR = 'backup/'  # where db backups are put
SCHEMA_DIR = 'schema/'
CACHE_DIR = 'scraper/cache/'  # used by scraper
DEFAULT_DATA_DIR = 'scraper/data/'  # used by scraper

#MongoDB
DB_NAME = 'csd'
SECRET_KEY = open("secret").read()

# allowing tokens to be moved to a different ip address could allow an
# attacker to more easily hijack a session, but not allowing it could require
# users to login more often
ALLOW_TOKENS_TO_CHANGE_IP = True

TOKEN_LENGTH = 20
SALT_LENGTH = 20
event = '2014ilch'

ALLOWED_ORIGINS = (
    'http://localhost:1111',
)

def make_json_error(ex):
    """
    creates json-parseable error messages such as:
    {"message": "405: Method Not Allowed"}
    """
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response

# for code in default_exceptions.iterkeys():
#     app.error_handler_spec[None][code] = make_json_error
