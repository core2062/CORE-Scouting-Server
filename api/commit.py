from werkzeug import exceptions as ex
import model.commit
import model.match
from helper import permission_required
#from jsonschema import ValidationError
from flask import g

"""api used for submitting commits"""


def mix(app):
	@app.route('/commit/submit', methods=["POST"])
	@permission_required()
	def submit_commit():
		a = g.args.copy()
		del a['token']
		return model.commit.commit(g.user, a)

	@app.route('/commit/schema')
	def schema():
		return model.commit.wrapper_schema

	@app.route('/commit/types')
	def types():
		return model.commit.types

	@app.route('/commit/type/<data_type>')
	def data_schema(data_type):
		if data_type not in model.commit.types:
			raise ex.NotFound("No data type %s. See /commit/types for a list of data types." % data_type)
		else:
			return getattr(model.commit, data_type + "_schema")

	@app.route('/commit/<commit>')
	def get_commit(commit):
		c = model.commit.Commit(commit)
		if not c:
			raise ex.NotFound('No commmit ' + commit)
		return c

#	@app.route('/match/<match_type>/<match_num>')
#	def get_match():
#		return Match(match_type, match_num)
