from mongo_descriptors import Db, MongoI
from bson.objectid import ObjectId
from werkzeug import exceptions as ex
from time import time
import re

from model.db import database as db
from collections import defaultdict
from config import CURRENT_EVENT


class Commit(object):
	db = Db(db['commits'])
	raw = MongoI()
	time = MongoI('time')

	###############
	public_attrs = ['user', 'data', 'data_type', 'enabled']
	user = MongoI('user')
	data = MongoI('data', dict)
	data_type = MongoI('data_type')
	enabled = MongoI('enabled', default=True)	# A boolean value telling whether or not this commit should be used

	def __init__(self, oi=None):
		oi = ObjectId(oi)  # Will get random ObjectId if oi is None.
		self.oi = oi

def commit(user, commit):
	c = Commit()
	for i in c.public_attrs:
		if i in commit:
			c.raw += {i: commit[i]}
	if not validate(c):
		
	return c


##############
# Validators for differnt types (Should call schema-specific validation)
##############
def validate_match(commit):
	is_team(commit.data['team'])
	is_match(commit.data['match'])
	is_true(commit.data['alliance'] in ['red', 'blue'], 'Alliance is not red or blue')
	try:
		is_regional(commit.data['regional'])
	except ex.BadRequest:
		d = commit.data
		d['regional'] = CURRENT_EVENT
		commit.data = d


#####################
# Validation utils
#####################
def is_true(val, exp):
	if not val:
		raise ex.BadRequest(exp)

MATCH_RE = re.compile(r"(p|q|qf|sf|f)(\d+)")


def is_match(val):
	match = MATCH_RE.match(val)
	if match is None:
		raise ex.BadRequest(str(val) + ' is not a valid match')


def is_team(team):
	if not db.sourceTeams.find_one({'team': team}):
		raise ex.BadRequest(str(team) + ' is not a valid team.')


def is_regional(regional):
	if not db.sourceEvent.find_one({'short_name': regional}):
		raise ex.BadRequest(str(regional) + 'is not a valid regional')
