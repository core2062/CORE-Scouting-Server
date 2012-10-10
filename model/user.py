from config import ALLOW_TOKENS_TO_CHANGE_IP, TOKEN_LENGTH, SALT_LENGTH, DEFAULT_PASSWORD, SCHEMA_DIR
from os import urandom
from jsonschema import validate
from simplejson import load
import hashlib
from time import time
from model.db import database as db
from copy import deepcopy

"""
	this module deals with all user data and authentication of the user
"""

# TODO: add guest user to setup script (same with admin)

GUEST_PERMISSIONS = [
	'no_email',  # guest email is fake - mail cannot be sent to it
]

STANDARD_PERMISSIONS = [
	'input',
	'modify_account_data',
#	'logout',  # guest cannot do this - it would screw up other people's sessions (not implemented)
]

ADMIN_PERMISSIONS = STANDARD_PERMISSIONS + [
	'reset_db',
]

USER_UPDATE_SCHEMA = load(open(SCHEMA_DIR + 'user_update.schema.json'))

		# if username != None and password != None:
		# 	self.authenticate_password(username, password, ip)
		# elif token != None:
		# 	self.authenticate_token(token, ip)
		# else:
		# 	raise Exception('not enough data provided to authenticate. a token or a username & password are required')


class User(object):
	"""
		this class is used to create a new instance of the user object (each object represents a single user)
		loads an empty user object by default. one of the authentication/loading methods should be used to load the user's data
	"""

	data = {
		#'_id': '',  # unique id (so it never changes) - mongo will assign this during saving if not assigned
		# must be sent to client (used to determine what options client can present), permissions that user has
		'permission': STANDARD_PERMISSIONS,
		# cannot be sent to client
		#'salt': '',
		#'hash': '',
		'log': [],  # should be sent to client (but perhaps truncated to certain length)
		#'session': {  # info about current session
		#	'ip': '',  # should not be sent to client
		#	'start_time': '',  # should not be sent to client, time when when token was issued
		#	'token': '',  # must be sent to client
		#},
		# (below) must be sent to client, basic info about user
		'prefs': {
			'fade': True,
		},
		'name': '',
		#'username': '',  # should be same as email, except for guest and admin
		#'email': '',
		#'team': 0,
	}

	def authenticate_token(self, token, ip):
		"""
		check token to authenticate user and load user data
		ip address should be provided to check aginst token if ALLOW_TOKENS_TO_CHANGE_IP == True
		"""

		query = {'session.token': token}  # base query (check token)

		if not ALLOW_TOKENS_TO_CHANGE_IP:
			query['session.ip'] = ip  # must match ip too (add to mongo query)

		user_data = db.user.find_one(query)

		if user_data == None:  # means nothing matched mongo query
			if ALLOW_TOKENS_TO_CHANGE_IP:
				raise Exception('incorrect info: token is incorrect')
			else:
				raise Exception('incorrect info: token is incorrect or was moved to a new IP address')

		self.data = user_data  # token is correct, load the user's data

	def authenticate_password(self, username, password, ip):
		"""authenticate user and make a token"""
		self.data = db.user.find_one({'username': username})

		if self.data == None:  # means nothing was returned from mongo query
			del self.data  # shouldn't keep data if login was wrong
			raise Exception('incorrect password or username')  # better to not say it was the username, to increase security

		# check password
		if self.get_hash(password) != self.data['hash']:
			del self.data  # shouldn't keep data if login was wrong
			raise Exception('incorrect password or username')  # better to not say it was the password, to increase security

		# check if currently logged in and run logout if true (and if user has permission to logout)
		# this is good because it creates a new session key during login, but it prevents users from logging into multiple computers
		# this is commented out for now
		#if self.has_permission('logout') and 'session' in self.data:
		#		self.logout()

		if not 'session' in self.data:
			# store session data if user is now logged out
			# the user not being logged out will cause the same token to be used for all logins to that account until logout is used
			self.data['session'] = {
				'token': urandom(TOKEN_LENGTH).encode('base64'),  # make a cryptographically secure random token
				'ip': ip,
				'start_time': time(),
			}

		self.save()  # save session data

	def get_hash(self, password):
		"""small function for getting a hash from a password & salt (the salt is read from the user's data)"""
		return hashlib.sha512(password + self.data['salt']).digest().encode('base64')

	def logout(self):
		"""
			logs-out current user by removing the session from the db
			a new token will be generated on the next login
		"""

		self.log('logout', self.data['session'])
		del self.data['session']
		self.save()

	def can(self, action):
		"""
			determines if user has permission to do a particular action
			this raises an error if the user doesn't have this permission
		"""
		if not self.has_permission(action):
			raise Exception('user does not have permission to ' + action)

	def has_permission(self, action):
		"""
			determines if user has permission to do a particular action
			this returns true or false
		"""
		return action in self.data['permission']

	def safe_data(self):
		"""returns data about user that is safe to give to client (it has passwords and unneeded info filtered out)"""
		safe_data = deepcopy(self.data)  # needs copy because it cuts stuff out

		del safe_data['_id']  # for internal use only
		del safe_data['username']  # client already knows username
		del safe_data['hash']
		del safe_data['salt']
		del safe_data['session']
		return safe_data

	def update(self, new_data):
		"""
			merges new_data into the user data and validates it
			this is also used for signup, because signing up is conceptually the same as an update plus changing the username
			also, if a password is put user.password it handles the generation of a new hash and salt (because passwords cannot be updated directly, like normal data is)
		"""
		self.can('modify_account_data')  # guest account cannot be changed

		# usernames cannot be changed directly, they are based on a user's email or assigned for special purposes like the guest account
		# _id is a unique value that is used by the database to connect actions and other stuff to user accounts, changing it would break a lot of stuff

		# add existing data (defaults)
		new_data = dict(
			{
				'prefs': self.data.get('prefs', None),
				'name': self.data.get('name', None),
				'email': self.data.get('email', None),
				'team': self.data.get('team', None),
			}.items() + new_data.items()
		)

		validate(new_data, USER_UPDATE_SCHEMA)

		if 'username' in new_data:
			self.can('change_username')

		if 'password' in new_data:
			self.data['salt'] = urandom(SALT_LENGTH).encode('base64')  # make a new salt (keep salts as unique as possible)
			self.data['hash'] = self.get_hash(new_data['password'])  # set a new password by changing the user's hash

		# stop email updates from changing to same email as another user
		if new_data['email'] != self.data.get('email', None):
			#NOTE: email is not currently checked to actually be real (by sending a confirmation email)... might want to add this
			if db.csd.user.find_one({'email': new_data['email']}) != None:
				raise Exception('the email specified is already in use by another user')
			elif not self.has_permission('change_username'):

				# change the username to match the new email
				new_data['username'] = new_data['email']

		self.data = dict(self.data.items() + new_data.items())  # TODO: add error reporting to tell if any part of merge fails

	def save(self):
		"""
			update the representation of the user object in mongo
			this is called at the end of the script????
			CONSIDER: switch to a transparent method of writing to the db
		"""
		db.user.save(self.data)

	def log(self, event, data):
		self.data['log'].append({
			'event': event,
			'data': data,
			'time': time(),
		})


def create_default_users():
	"""
		put the default users (guest and admin) directly into the database
		while resetting/setting up the database
	"""

	user = User()

	user.update({
		'email': 'admin@email.com',
		'team': 2062,
		'password': DEFAULT_PASSWORD,
	})

	user.data['username'] = 'admin'
	user.data['permission'] = ADMIN_PERMISSIONS
	user.save()

	user = User()

	user.update({
		'email': 'guest@email.com',
		'team': 2062,
		'password': DEFAULT_PASSWORD,
	})

	user.data['username'] = 'guest'
	user.data['permission'] = GUEST_PERMISSIONS
	user.save()
