from flask import jsonify
#from werkzeug import exceptions as ex
from override_flask import NewFlask as Flask
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

app = Flask(__name__)

#filesystem

# get current working directory (top level of the csd server folder)
app.config["BACKUP_DIR"] = 'backup/'  # where db backups are put
app.config["SCHEMA_DIR"] = 'schema/'
app.config["CACHE_DIR"] = 'scraper/cache/'  # used by scraper
app.config["DEFAULT_DATA_DIR"] = 'scraper/data/'  # used by scraper

#MongoDB
app.config["DB_NAME"] = 'csd'

# allowing tokens to be moved to a different ip address could allow an
# attacker to more easily hijack a session, but not allowing it could require
# users to login more often
app.config["ALLOW_TOKENS_TO_CHANGE_IP"] = True

app.config["TOKEN_LENGTH"] = 20
app.config["SALT_LENGTH"] = 20

#only used while setting up db (for guest & admin account)
#admin password should be changed directly after setting up db
app.config["DEFAULT_PASSWORD"] = 'guest'

# temporary (for development). the client will determine this in the future
app.config["CURRENT_EVENT"] = 'wi'

app.config["ALLOWED_ORIGINS"] = (
    'http://localhost:1111',
)

jinja_env = jinja2.Environment(
    trim_blocks = True,
    lstrip_blocks = True
)

def make_json_error(ex):
    """
    creates json-parseable error messages such as:
    {"message": "405: Method Not Allowed"}
    """
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response

for code in default_exceptions.iterkeys():
    app.error_handler_spec[None][code] = make_json_error
