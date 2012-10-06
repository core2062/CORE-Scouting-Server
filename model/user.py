from config import ALLOW_TOKENS_TO_CHANGE_IP, TOKEN_LENGTH, SALT_LENGTH, DEFAULT_PASSWORD
from os import urandom
import hashlib
from time import time
from model.db import database as db
from copy import deepcopy
import re
from helper import restrictive_merge

"""
	this module deals with all user data and authentication of the user
"""

# TODO: add guest user to setup script (same with admin)

EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")

GUEST_PERMISSIONS = [
	'no_email',  # guest email is fake - mail cannot be sent to it
]

STANDARD_PERMISSIONS = [
	'input',
	'modify_account_data',
	'logout',  # guest cannot do this - it would screw up other people's sessions
]

ADMIN_PERMISSIONS = STANDARD_PERMISSIONS + [
	'reset_db',
]

		# if username != None and password != None:
		# 	self.authenticate_password(username, password, ip)
		# elif token != None:
		# 	self.authenticate_token(token, ip)
		# else:
		# 	raise Exception('not enough data provided to authenticate. a token or a username & password are required')


class Instance(object):
	"""
		this class is used to create a new instance of the user object (each object represents a single user)
		loads an empty user object by default. one of the authentication/loading methods should be used to load the user's data
	"""

	data = {
		#'_id': '',  # unique id (so it never changes) - mongo will assign this during saving if not assigned
		# must be sent to client (used to determine what options client can present), permissions that user has
		'permission': STANDARD_PERMISSIONS,
		'session': {  # info about current session
			'ip': '',  # should not be sent to client
			'start_time': '',  # should not be sent to client, time when when token was issued
			'token': '',  # must be sent to client
		},
		'prefs': {  # must be sent to client, used to store preferences
			'fade': True,
		},
		# cannot be sent to client
		'salt': '',
		'hash': '',
		# must be sent to client, basic info about user
		'name': '',
		'username': '',  # should be same as email, except for guest and admin
		'email': '',
		'team': 0,
		'log': [],  # should be sent to client (but perhaps truncated to certain length)
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
				'token': urandom(TOKEN_LENGTH),  # make a cryptographically secure random token
				'ip': ip,
				'start_time': time(),
			}

		self.save()  # save session data

	def get_hash(self, password):
		"""small function for getting a hash from a password & salt (the salt is read from the user's data)"""
		return hashlib.sha512(password + self.data['salt']).hexdigest()

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
		if not action in self.data['permission']:
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
		del safe_data['username']  # client already knows username
		del safe_data['hash']
		del safe_data['salt']
		del safe_data['session']
		return safe_data

	def update(self, new_data):
		"""
			merges new_data into the user data and validates it
			this is also used for signup, because signing up is conceptually the same as an update plus changing the username
			also, if a password is put user.password it handles the generation of a new hash and salt (because passwords cannot be updated directly, the same way normal data is)
			this does not save to the db (since it is used for signup, which uses the guest account and needs to save on its own) - call self.save() after all updating
		"""
		#if '_id' in new_data:
		#	# _id is a unique value that is used by the database to connect actions and other stuff to user accounts, changing it would break a lot of stuff
		#	raise Exception('_id cannot be changed')

		#CONSIDER: replace check for username and _id with limit by JSON schema

		#if 'username' in new_data:
		#	# maybe option to change usernames could be added later
		#	raise Exception('usernames cannot be changed directly, they are based on a user\'s email or assigned for special purposes like the guest account')

		# validate data aginst schema !!!!!!!!!!!!!!!!!!!!!!!!!!!!!

		if 'password' in new_data:
			# make a new salt (keep salts as unique as possible)
			self.data['salt'] = urandom(SALT_LENGTH)

			# set a new password by changing the user's hash
			self.data['hash'] = self.get_hash(new_data['password'])

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

		# use regular merge !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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


def create_default_users():
	"""
		put the default users (guest and admin) directly into the database
		while resetting/setting up the database
	"""

	salt = urandom(SALT_LENGTH)

	db.user.save({
		'salt': salt,
		'hash': hashlib.sha512(DEFAULT_PASSWORD + salt).hexdigest(),
		'permission': GUEST_PERMISSIONS,
		'prefs': {
			'fade': True,
		},
		'name': '',
		'username': 'guest',
		'email': '',
		'team': 0,
		'log': [],
	})

	db.user.save({
		'salt': salt,
		'hash': hashlib.sha512(DEFAULT_PASSWORD + salt).hexdigest(),
		'permission': ADMIN_PERMISSIONS,
		'prefs': {
			'fade': True,
		},
		'name': '',
		'username': 'admin',
		'email': '',
		'team': 0,
		'log': [],
	})

# TODO: write in json schema
