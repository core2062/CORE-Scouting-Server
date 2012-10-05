from config import ALLOW_TOKENS_TO_CHANGE_IP
import uuid
import hashlib
from time import time
from db import database as db
from copy import deepcopy
import re
from helper import restrictive_merge

"""
	this module deals with all user data and authentication of the user
"""

# TODO: add guest user to setup script (same with admin)

EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")

STANDARD_PERMISIONS = []
GUEST_PERMISIONS = []
ADMIN_PERMISIONS = []


class Instance(object):
	""" this class is used to create a new instance of the user object (each object represents a single user) """

	def __init__(self, ip, username=None, password=None, token=None):
		"""
		used to authenticate user
		checks username & password or token and if correct, puts the user object in data
		if an error occurs in this part, the client must run its logout function
		"""
		if username != None and password != None:
			# authenticate user and make a token
			self.data = db.user.find_one({'_id': username})

			if self.data == None:  # means nothing was returned from mongo query
				raise Exception('incorrect password or username')  # better to not say it was the username, to increase security

			# check password
			if self.get_hash(password) != self.data.authentication.hash:
				del self.data  # shouldn't keep data if login was wrong
				raise Exception('incorrect password or username')  # better to not say it was the password, to increase security

			#check if currently logged in and run logout if true

			# store session data
			self.data['session']['token'] = re.sub('-', '', str(uuid.uuid4()))  # make a unique id & remove the dashes (they are useless)
			self.data['session']['ip'] = ip
			self.data['session']['start_time'] = time()
			self.save()  # save session data

		elif token != None:
			# check token to authenticate user
			query = {'session.token': token}  # base query (check token)

			if not ALLOW_TOKENS_TO_CHANGE_IP:
				query['session.ip'] = ip  # must match ip too

			self.data = db.user.find_one(query)

			if self.data == None:  # means nothing was returned from mongo query
				if ALLOW_TOKENS_TO_CHANGE_IP:
					raise Exception('incorrect info: token is incorrect')
				else:
					raise Exception('incorrect info: token is incorrect or was moved to a new IP address')

		else:
			raise Exception('not enough data provided to authenticate. a token or a username & password are required')

	# TODO: write in json schema

	# defaults = {
	# 	'_id': '',  # unique id (so it never changes)
	# 	'authentication': {  # cannot be sent to client
	# 		'salt': '',
	# 		'hash': '',
	# 	},
	# 	'permission': [  # must be sent to client (used to determine what options client can present), permissions that user has
	# 		'input',
	# 	],
	# 	'session': {  # info about current session
	# 		'ip': '',  # should not be sent to client
	# 		'start_time': '',  # should not be sent to client, time when when token was issued
	# 		'token': '',  # must be sent to client
	# 	},
	# 	'prefs': {  # must be sent to client, used to store preferences
	# 		'fade': True,
	# 		'verbose': True,
	# 	},
	# 	# must be sent to client, basic info about user
	# 	'first_name': '',
	# 	'last_name': '',
	# 	'username': '',  # should be same as email, except for guest and admin
	# 	'email': '',
	# 	'team': 0,
	# 	# should not be sent to client, optional info ... probably wouldn't matter if it was sent to client
	# 	'zip': '',
	# 	'browser': '',
	# 	'gender': '',
	# 	'log': [],  # should be sent to client (but perhaps truncated to certain length)
	#}

	def get_hash(self, password):
		"""small function for getting a hash from a password & salt (the salt is read from the user's data)"""
		return hashlib.sha512(password + self.data.authentication.salt).hexdigest()

	def logout(self):
		"""logs out current user by removing session from db"""

		self.log('logout', self.data.session)
		del self.data.session
		self.save()

	def can(self, action):
		"""
			determines if user has permission to do a particular action
			this raises an error if the user doesn't have this permission
		"""
		if not action in self.data['permission']:
			raise Exception('user does not have permission to ' + action)

	def safe_data(self):
		"""returns data about user that is safe to give to client (it has passwords and unneeded info filtered out)"""
		safe_data = deepcopy(self.data)  # needs copy because it cuts stuff out
		del safe_data['username']  # client already knows username
		del safe_data['authentication']
		del safe_data['opt']
		del safe_data['session']['ip']
		del safe_data['session']['start_time']
		return safe_data

	def update(self, new_data):
		"""
			merges new_data into the user data and validates it
			this is also used for signup, because signing up is conceptually the same as an update plus changing the username
			also, if a password is put user.authentication.password it handles the generation of a new hash and salt (because passwords cannot be updated directly, the same way normal data is)
			this does not save to the db (since it is used for signup, which uses the guest account and needs to save on its own) - call self.save() after all updating
		"""
		if '_id' in new_data:
			# _id is a unique value that is used by the database to connect actions and other stuff to user accounts, changing it would break a lot of stuff
			raise Exception('_id cannot be changed')

		#CONSIDER: replace check for username and _id with limit by JSON schema

		if 'username' in new_data:
			# maybe option to change usernames could be added later
			raise Exception('usernames cannot be changed directly, they are based on a user\'s email or assigned for special purposes like the guest account')

		if 'email' in new_data:
			# even guest and admin accounts can set an email. they need to during signup and their changes are not saved to the database anyway

			# stop email updates from changing to same email as another user
			if new_data['email'] == self.data['email']:
				del new_data['email']  # not changing the email, so it can just be omitted (although it shouldn't really be sent in the first place if it is not changing)
			elif db.csd.user.find_one({'email': new_data['email']}) != None:
				raise Exception('the email specified is already in use by another user')
			else:  # validate email
				if EMAIL_RE.match(new_data['email']) == None:
					raise Exception('the email specified is not a valid email address')
				#NOTE: email is not currently checked to actually be real (by sending a confirmation email)... might want to add this

				# change the username to match the new email
				new_data['username'] = new_data['email']

		# validate other data aginst schema

		self.data = restrictive_merge(new_data, self.data)  # TODO: add error reporting to tell if any part of merge fails

	def save(self):
		"""
			update the representation of the user object in mongo
			this is called at the end of the script????
			CONSIDER: switch to a transparent method of writing to the db
		"""
		self.can('modify_account_data')  # guest account cannot be changed
		db.user.save(self.data)

	def log(self, event, data):
		self.data.append({
			'event': event,
			'data': data,
			'time': time(),
		})
