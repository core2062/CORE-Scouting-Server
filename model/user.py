import uuid
import time
import db as db
from copy import deepcopy
import re
import model.helper as helper

"""
	this module deals with all user data and authentication of the user
"""

# def __getitem__(self, key):
# 	print '(get)', ' key:', key
# 	return self.key

# def __setitem__(self, key, value):
# 	print '(set)', ' key:', key, ' value:', value

# 	#code to update mongo goes here

# 	self.key = value

# def __delitem__(self, key):
# 	print '(delete)', ' key:', key
# 	del self.key


class Instance(object):
	""" this class is used to create a new instance of the user object (each object represents a single user) """

	defaults = {  # initialized with defaults (for guest user)
		'_id': 'guest',
		'account': {  # cannot be sent to client
			'password': '',
			'email': '',
		},
		'permission': [  # must be sent to client (used to determine what options client can present), permissions that user has
			'input',
		],
		'info': {  # must be sent to client, basic info about user
			'fName': '',
			'lName': '',
			'team': 0,
		},
		'prefs': {  # must be sent to client, used to store preferances
			'fade': True,
			'verbose': True,
		},
		'opt': {  # should not be sent to client, optional info ... probably wouldn't matter if it was sent to client
			'zip': '',
			'browser': '',
			'gender': '',
		},
		'session': {  # info about current session
			'ip': '',  # should not be sent to client
			'startTime': '',  # should not be sent to client, time when when token was issued
			'token': '',  # must be sent to client
		},
		'log': {},  # should be sent to client (but perhaps truncated to certain length)
	}

	def check(self, username, token, ip):
		"""
			checks username & token and if correct, puts the user object in data
			used to authenticate user is already logged in (has a token)
			if an error occurs in this part, the client must run its logout function
		"""

		#put it in a temporary variable in case it is incorrect - shouldn't load the user until they are correctly logged in
		tmpUser = db.csd.user.find_one({'_id': username, 'session.token': token, 'session.ip': ip})

		if tmpUser == None:  # means nothing was returned from mongo query
			raise Exception('incorrect info')  # username & token & ip combo are not correct
			#CONSIDER: add explanation for why check failed (if it was ip or token or username)

		self.load(tmpUser)  # inputs are correct, put user object in correct place

	def login(self, username, password, ip):
		"""
			checks username & password and if correct, generates a token and puts user object in data
			used when user is not yet logged in (has no token)
			users cannot be logged in on multiple ip addresses and multiple users cannot be on same ip
		"""

		#put user data in a temp variable in case it is incorrect - shouldn't load the user until they are correctly logged in
		tmpUser = db.csd.user.find_one({
			'_id': username,
			'account.password': password,
		})

		if tmpUser == None:  # means nothing was returned from mongo query
			raise Exception('incorrect info')  # better to only say "incorrect info" to increase security

		self.load(tmpUser)  # inputs are correct, put user object in correct place

		#CONSIDER: check if currently logged in and run logout if true?

		#zero out ip & token for users w/ same ip
		db.csd.user.update(
			{
				'ip': self.data['session']['ip']
			},
			{
				'$unset': {
					'session.ip': 1,
					'session.token': 1,
				}
			},
		)

		self.data['session']['token'] = re.sub('-', '', str(uuid.uuid4()))  # make a unique id & remove the dashes (they are useless)
		self.data['session']['ip'] = ip
		self.data['session']['startTime'] = time.time()

		self.save()  # save session data

	def logout(self):
		"""logs out current user by removing ip & token from db"""
		return 'logout code not finished'

	def can(self, action):
		"""determines if user has permission to do a particular action (returns true or false)"""
		return action in self.data['permission']

	def load(self, user_data):
		"""merges user_data with defaults and puts it in the correct place"""
		self.data = dict(deepcopy(self.defaults).items() + user_data.items())

	def safe_data(self):
		"""returns data about user that is safe to give to client (it has passwords and unneeded info filtered out)"""
		safeData = deepcopy(self.data)  # needs copy because it cuts stuff out
		del safeData['account']
		del safeData['opt']
		del safeData['session']['ip']
		del safeData['session']['startTime']
		return safeData

	def update(self, new_data):
		"""
			merges new_data into the user data and validates it
			this is also used for signup, because signing up is conceptually the same as an update
		"""

		if '_id' in new_data:  # stop username updates from overwriting other users
			if new_data['_id'] == self.data['_id']:
				del new_data['_id']  # not changing the _id, so it can just be omitted
			elif db.csd.user.find_one({'_id': new_data['_id']}) != None:  # another user exists with this username
				raise Exception('the username specified is already in use by another user')

		self.data = helper.restrictive_merge(new_data, self.data)  # CONSIDER: add error reporting to tell if any part of merge fails

	def validate_data(self):
		"""validates user.data - intended to be used for signup and user info changes to determine if user data is acceptable"""
		return 'validateData not finished'

	def save(self):
		"""
			update the representation of the user object in mongo - this is called at the end of the script
			consider switching to a transparent method of writing to the db
		"""
		if self.data['_id'] != 'guest':  # shouldn't save guest account to db because guest isn't a real user
			db.csd.user.save(helper.remove_defaults(self.data, self.defaults))  # save with defaults cut out

	# abc = user()
	# abc.data['permission'] = 'the stuff'
	# abc.data['account'] = {'pword': 'the stuff'}
	# print abc.data['account']['pword']
	# abc.data['account']['pword'] = 'fffdf'
	# print abc.data['account']['pword']
	# print abc.can('input')
