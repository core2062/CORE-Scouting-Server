
"""api used for submitting commits"""

from werkzeug import exceptions as ex
import model.commit
from helper import permission_required
from jsonschema import ValidationError
from flask import g


def mix(app):
	
	@app.route('/commit/match', methods=["POST"])
	@permission_required()
	def commit_match():
		a = g.args.copy()
		del a['token']
		try:
			model.commit.validate(a)
		except ValidationError:
			raise ex.BadRequest("Doesn't match schema. See /commit/schema for a copy.")
		return model.commit.commit(g.user, a)

	@app.route('/commit/schema')
	def schema():
		return model.commit.schema