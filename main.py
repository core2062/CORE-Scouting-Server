from flask import g, request, jsonify
#from werkzeug import exceptions as ex
from override_flask import NewFlask as Flask
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from simplejson import loads
import os

#from helper import permission_required
#import model.db as db
import api

"""
...this file holds configuration variables for the csd. these variables are used
throughout the code, but are stored here to make changing configuration
easier.
"""

app = Flask(__name__)

#filesystem

# get current working directory (top level of the csd server folder)
app.config["CWD"] = os.path.dirname(__file__) + '/'

app.config["BACKUP_DIR"] = app.config["CWD"] + 'backup/'  # where db backups are put
app.config["SCHEMA_DIR"] = app.config["CWD"] + 'schema/'
app.config["CACHE_DIR"] = app.config["CWD"] + 'scraper/cache/'  # used by scraper
app.config["DEFAULT_DATA_DIR"] = app.config["CWD"] + 'scraper/data/'  # used by scraper

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

app.config["CURRENT_EVENT"] = 'wi'  # temporary (for development). the client will determine this in the future


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

api.mix(app, ['commit', 'user', 'beverages'])


@app.before_request
def before_request():
	# put the request args in a mutable dict so we can pre-process them
	g.args = dict(request.args.to_dict())

	if request.json:
		# if json is sent, merge that into the args
		g.args.update(request.json)
	# below stuff (g.notify & g.error) isn't really used... consider removing
	# an array that holds notifications (like non-fatal errors or important messages)
	#g.notify = []


# @app.after_view
# def after_view(rv):
# 	# check to see that it's json, if not then return
# 	if not type(rv) in (dict, list):
# 		return
# 	#put stuff from g in response
# 	return


@app.route('/')
def index():
	# Eventually, return auto-gen sitemap.
	return {"message": "huh."}


@app.route('/schema/<name>')
def schema(name):
	"""return a schema from the schema dir as a dict (so it'll be sent as json)"""
	return loads(
		open(os.path.join(app.config["SCHEMA_DIR"] + '%s.schema.json' % name)).read()
	)


if __name__ == "__main__":
	app.run(debug=True)
