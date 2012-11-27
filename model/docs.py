from mongo_descriptors import Db, MongoI
from bson.objectid import ObjectId
from werkzeug import exceptions as ex
from time import time
import re

from model.db import database as db
from collections import defaultdict
from config import CURRENT_EVENT


class Commit(object):
	"""
		this object represents a single change to a document
		one or more commit(s) compile into a document
	"""
	db = Db(db['commits'])

	# _id of user (assigned on submission based on token)
	user = MongoI('user')

	# holds the json that is the commit - the parts of the doc that are
	# updated (or the entire doc if it's new)
	data = MongoI('data', dict)

	# the schema that will be used to validate the data, and the type of doc
	# that it compiles into ex: pitdata, matchdata, scraped_data
	data_type = ''

	# a boolean value telling whether or not this commit should be used
	enabled = MongoI('enabled')

	# unix time of commit (assigned on submission). this tells the order in
	# which commits will be compiled into each other
	time = MongoI('time')

	# this identifies the document that the commit goes to (the _id of the
	# doc). it is assigned on submission (as a random string, if this is the
	# first commit in a doc) or provided (if it is a update to an existing
	# doc)
	doc_id = ''

	raw = MongoI()

	def __init__(self, oi=None):
		oi = ObjectId(oi)  # Will get random ObjectId if oi is None.
		self.oi = oi

	def validate(self):
		"""
		validate self.data based on the schema that self.data_type indicates
		"""
		if not self.type:
			raise ex.BadRequest('No type in commit')
		if not self.data:
			raise ex.BadRequest('No data in commit')
		if not self.enabled:
			#enable commits by default
			commit['enabled'] == True
		if not "validate_" + str(self.data_type) in globals().keys():
			ex.BadRequest('Unknown type')

		#pass data through json schema, based on self.data_type


def commit(user, commit):
	"""
	create a commit. this isn't the __init__ method for the commit because not
	all commits are to be loaded this way
	"""
	commit = defaultdict(lambda: None, commit)

	c = Commit()
	c.user = user.oi
	c.data = commit['data']
	c.time = time()
	c.enabled = commit['enabled']

	c.validate()
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
