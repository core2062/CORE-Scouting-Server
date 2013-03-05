from mongo_descriptors import Db, MongoI
from bson.objectid import ObjectId
from werkzeug import exceptions as ex
from time import time
import re

from model.db import database as db
import model.user
from collections import defaultdict
from config import CURRENT_EVENT
import jsonschema
from jsonschema import ValidationError
import simplejson as json
import functools



class Commit(object):
	db = Db(db=db['commits'])
	raw = MongoI()

	###############
	public_attrs = ['user','time', 'data', 'data_type', 'enabled']
	user = MongoI('user')
	time = MongoI('time')
	data = MongoI('data', dict)
	data_type = MongoI('data_type')
	enabled = MongoI('enabled', default=True)	# A boolean value telling whether or not this commit should be used

	def __init__(self, oi=None, create=False):
		self.oi = ObjectId(oi)  # Will get random ObjectId if oi is None.
		if not self.db.find_one(self.oi):
			self.db.insert({"_id": self.oi})

	def __json__(self):
		ret = {'id': str(self.oi)}
		for i in self.public_attrs:
			ret[i]= getattr(self, i)
		return ret

	def disable(self):
		self.enabled = False

	def remove(self):
		del self.raw

def commit(user, commit):
	try:
		validate_wrapper(commit)
	except ValidationError, e:
		raise ex.BadRequest("Doesn't match schema. See /commit/schema for a copy." + str(e))
	try:
		validate_data_type(commit['data_type'], commit['data'])
	except ValidationError, e:
		raise ex.BadRequest("Doesn't match "+commit['data_type']+" schema. See /commit/type/"+commit['data_type']+" for a copy. "+str(e))

	c = Commit(create = True)

	for i in c.public_attrs:
		if i in commit:
			c.raw += {i: commit[i]}
	c.time = time()
	c.user = user.oi
	return c

def find(expr):
	for i in db['commits'].find(expr, fields=[]):
		yield Commit(i['_id'])

def find_one(expr):
	return Commit(db['commits'].find_one(expr, fields=[])["_id"])

def by_user(user):
	if hasattr(user,'oi'):
		user = user.oi

	return (Commit(i['_id']) for i in db['commits'].find({'user':user}, fields=[]))

def validate_data_type(data_type, data):
	if data_type in types:
		globals()["validate_"+str(data_type)](data)
	else:
		raise ex.BadRequest("Not a type. See /commit/types for types of data input.")

types = ['match']
wrapper_schema = json.load(open('schema/commit.schema.json'))
validate_wrapper = functools.partial(jsonschema.validate, wrapper_schema)
match_schema = json.load(open('schema/match.schema.json'))
validate_match = functools.partial(jsonschema.validate, match_schema)

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
# 		d['regional'] = CURRENT_EVENT
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
