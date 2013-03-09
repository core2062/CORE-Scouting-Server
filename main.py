from config import app
from flask import g, request, send_from_directory
from simplejson import loads
import os

from model.db import database as db
from helper import allow_origins, check_args
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

	# if POST args or json are sent, merge that into the args
	if request.json:
		g.args.update(request.json)
	if request.form:
		g.args.update(request.form.to_dict())

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


@app.route('/submit', methods=['POST'])
@allow_origins
def submit():
	check_args('data')
	data = {
		"comment": "",
		"disabled": False,
		"penalties_yellow": 0,
		"shoots": False,
		"tech_fouls": 0,
		"match_num": 0,
		"no_show": False,
		"climb_attempt": 0,
		"climbs": False,
		"pyramid": 0,
		"high": 0,
		"middle": 0,
		"low": 0,
		"miss": 0,
		"auto_high": 0,
		"auto_middle": 0,
		"auto_low": 0,
		"auto_miss": 0,
		"fouls": 0,
		"defends": False,
		"penalties_red": 0,
		"team": 0,
		"floor_pickup": False
	}
	data.update(loads(g.args['data']))
	db.scouting.insert(data)
	return {"message": "J\'AIME VOTRE DATA"}


@app.route('/matches.csv')
def make_csv():
	matches = db.scouting.find({'match_type': 'q'})
	cols = [
		"comment",
		"disabled",
		"penalties_yellow",
		"shoots",
		"tech_fouls",
		"match_num",
		"no_show",
		"climb_attempt",
		"climbs",
		"pyramid",
		"high",
		"middle",
		"low",
		"miss",
		"auto_high",
		"auto_middle",
		"auto_low",
		"auto_miss",
		"fouls",
		"defends",
		"penalties_red",
		"team",
		"floor_pickup",
	]
	rows = []
	for match in matches:
		del match['_id']
		try:
			del match['auto_pyramid']
		except:
			pass
		row = [None] * 30
		for k, v in match.items():
			if not k in cols:
				cols += [k]
			row[cols.index(k)] = v
		rows += [row]
	output = ''
	for line in ([cols] + rows):
		new_line = []
		for item in line:
			new_line += [str(item).replace(',', ';').replace('\r\n', '\n').replace('\n', ' | ')]
		output += ','.join(new_line) + '\n'
	open(app.config['CWD'] + 'matches.csv', 'w').write(output)
	return send_from_directory(app.config['CWD'], 'matches.csv')


@app.route('/schema/<name>')
@allow_origins
def schema(name):
	"""return a schema from the schema dir as a dict (so it'll be sent as json)"""
	return loads(
		open(os.path.join(app.config["SCHEMA_DIR"] + '%s.schema.json' % name)).read()
	)


if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0")
