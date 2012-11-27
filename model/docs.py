# This is from your github comment.
  #	  _id: unique id of commit (assigned on submission)
  #	  time: unix time of commit (assigned on submission)
  #	   - this tells the order in which they will be compiled into each other
  #	  user: _id of user (assigned on submission based on token)
  #	  type: the schema that will be used to validate the data.
  #	   - this tells the type of data... ex: pitdata, matchdata, scraped_data
  #	  data: holds the json that is the commit
  #	  enabled: a boolean value telling whether or not this commit should be used 

# Not used:
  #   doc_id: unique id of document (assigned on submission or provided) *(huh?)*

from model.db import database as db
from mongo_descriptors import Db, MongoI
from collections import defaultdict
from bson.objectid import ObjectId
from time import time
from werkzeug import exceptions as ex

class Commit(object):
	db = Db(db['commits'])
	user = MongoI('user')
	data = MongoI('data', dict)
	enabled = MongoI('enabled')
	time = MongoI('time')

	raw = MongoI()
	def __init__(self, oi=None):
		oi = ObjectId(oi)	# Will get random ObjectId if oi is None.
		self.oi = oi

def commit(user, commit):
	commit = defaultdict(lambda: None, commit)

	########
	# This could be replaced by a generic commit schema.
	########
	if not commit['type']:
		raise ex.BadRequest('No type in commit')
	if not commit['data']:
		raise ex.BadRequest('No data in commit')
	if not commit['enabled']:
		commit['enabled'] == True

	if not "validate_"+str(commit['type']) in globals().keys():
		ex.BadRequest('Unknown type')
	c = Commit()
	c.user = user.oi
	c.data = commit['data']
	c.time = time()
	c.enabled = commit['enabled']
	globals()["validate_"+str(commit['type'])](c)

##############
# Validators for differnt types (Should call schema-specific validation)
##############

def validate_match(commit):
	is_team(commit.data['team'])
	is_match(commit.data['match'])
	is_true(commit.data['alliance'] in ['red','blue'], 'Alliance is not red or blue')
	try:
	 	is_regional(commit.data['regional']):
	 except ex.BadRequest:
	 	d = commit.data
	 	d['regional'] = CURRENT_EVENT
	 	commit.data = d

#####################
# Validation utils 
#####################

def is_true(val,exp):
	if not val:
		raise ex.BadRequest(exp)

matchre = re.compile(r"(p|q|qf|sf|f)(\d+)")
def is_match(val):
	match = matchre.match(val)
	if match is None:
		raise ex.BadRequest(str(val)+' is not a valid match')

def is_team(team):
	if not db.sourceTeams.find_one({'team':team}):
		raise ex.BadRequest(str(team)+' is not a valid team.')

def is_regional(regional):
	if not db.sourceEvent.find_one('short_name':regional):
		raise ex.BadRequest(str(regional)+'is not a valid regional')