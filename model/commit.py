
from werkzeug import exceptions as ex
from datetime import datetime
#import re

from config import app
from model.db import database as db
import jsonhelper
#from collections import defaultdict
import jsonschema; from jsonschema import ValidationError
import simplejson as json
import mongoengine as me
import os.path


class Commit(me.DynamicDocument):

	time = me.DateTimeField(default=datetime.now)
	data_type = me.StringField()
	enabled = me.BooleanField(default=True)
	user = me.StringField()

def find(expr):
	raise Exception("update needed")

	for i in db['commits'].find(expr, fields=[]):
		yield Commit(i['_id'])


def find_one(expr):
	raise Exception("update needed")

	return Commit(db['commits'].find_one(expr, fields=[])["_id"])


def by_user(user):
	raise Exception("update needed")

	if hasattr(user, '_id'):
		user = user.oi
	return (Commit(i['_id']) for i in db['commits'].find({'user': user}, fields=[]))


def validate_data_type(data_type, data):
	if data_type in types:
		jsonschema.validate(data, types[data_type])
	else:
		raise ex.BadRequest("Not a type. See /commit/types for types of data input.")

types = {
	'match': json.loads(jsonhelper.remove_comments(
		open(os.path.join(app.config["SCHEMA_DIR"], 'match.schema.json')).read()))
}


# ##############
# # Validators for differnt types (Should call schema-specific validation)
# ##############
# def validate_match(commit):
# 	is_team(commit.data['team'])
# 	is_match(commit.data['match'])
# 	is_true(commit.data['alliance'] in ['red', 'blue'], 'Alliance is not red or blue')
# 	try:
# 		is_regional(commit.data['regional'])
# 	except ex.BadRequest:
# 		d = commit.data
# 		d['regional'] = app.config["CURRENT_EVENT"]
# 		commit.data = d


# #####################
# # Validation utils
# #####################
# def is_true(val, exp):
# 	if not val:
# 		raise ex.BadRequest(exp)

# MATCH_RE = re.compile(r"(p|q|qf|sf|f)(\d+)")


# def is_match(val):
# 	match = MATCH_RE.match(val)
# 	if match is None:
# 		raise ex.BadRequest(str(val) + ' is not a valid match')


# def is_team(team):
# 	if not db.sourceTeams.find_one({'team': team}):
# 		raise ex.BadRequest(str(team) + ' is not a valid team.')


# def is_regional(regional):
# 	if not db.sourceEvent.find_one({'short_name': regional}):
# 		raise ex.BadRequest(str(regional) + 'is not a valid regional')
