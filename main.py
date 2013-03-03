from flask import g, request, jsonify
#from werkzeug import exceptions as ex
from override_flask import NewFlask as Flask
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

from config import CURRENT_EVENT
from helper import permission_required
#import model.db as db

import api


def make_json_error(ex):
	"""
	creates json-parseable error messages such as:
	{"message": "405: Method Not Allowed"}
	"""
	response = jsonify(message=str(ex))
	response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
	return response

app = Flask(__name__)

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


@app.route('/admin/reset', methods=['DELETE'])
@permission_required('reset_db')
def reset_db():
   db.clear()
   db.defaults()
   return {'message': 'reset successful'}


@app.route('/admin/scrape', methods=['POST'])
@permission_required()
def scrape():
	from scraper import scraper
	scraper.event_names()
	scraper.event_details()
	scraper.tpids()
	scraper.team_details()
	scraper.match(CURRENT_EVENT)
	return {'message': 'scrape successful'}

if __name__ == "__main__":
	app.run(debug=True)
