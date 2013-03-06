from config import app
from flask import g, request
from simplejson import loads
import os

#import model.db as db
from helper import allow_origins
import api.commit
import api.user
import api.beverages

api.commit.mix(app)
api.user.mix(app)
api.beverages.mix(app)


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
@allow_origins
def schema(name):
	"""return a schema from the schema dir as a dict (so it'll be sent as json)"""
	return loads(
		open(os.path.join(app.config["SCHEMA_DIR"] + '%s.schema.json' % name)).read()
	)


if __name__ == "__main__":
	app.run(debug=True)
