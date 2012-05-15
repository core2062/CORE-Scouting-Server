import pymongo
import uuid
import time
import web

c = pymongo.Connection()
db = c.csd


class user:
	"""
		this class deals with all user data and authentication of the user
	"""
	"""
	def __getitem__(self, key):
		print '(get)', ' key:', key
		return self.key

	def __setitem__(self, key, value):
		print '(set)', ' key:', key, ' value:', value

		#code to update mongo goes here

		self.key = value

	def __delitem__(self, key):
		print '(delete)', ' key:', key
		del self.key
	"""
	data = {  # initialized with defaults (for guest user)
		'_id': 'guest',
		'account': {
			'password': '',
			'email': '',
		},
		'permission': [  # list of permissions that user has
			'input',
		],
		'info': {
			'fName': '',
			'lName': '',
			'team': 0,
		},
		'prefs': {
			'fade': True,
			'verbose': True,
		},
		'opt': {  # optional info
			'zip': '',
			'browser': '',
			'gender': '',
		},
		'session': {  # info about current session
			'ip': '',
			'startTime': '',  # time when when token was issued
			'token': '',
		},
		'log': {},
	}

	def check(self, username, token):
		"""
			checks username & token and if correct, puts the user object in data
			used to authenticate user is already logged in (has a token)
			if an error occurs in this part, the client must run its logout function
		"""

		#put it in a temporary variable in case it is incorrect - shouldn't load the user until they are correctly logged in
		tmpUser = db.user.find_one({'_id': username, 'session.token': token, 'session.ip': web.ctx.ip})

		if tmpUser == None:  # means nothing was returned from mongo query
			raise Exception('incorrect info')  # username & token & ip combo are not correct
			#CONSIDER: add explanation for why check failed (if it was ip or token or username)

		self.data = tmpUser  # inputs are correct, put user object in correct place

	def login(self, password, username='', email=''):
		"""
			checks username / email & password and if correct, generates token and puts user object in data
			used when user is not yet logged in (has no token)
			can login with either email or username
			users cannot be logged in on multiple ip addresses and multiple users cannot be on same ip
		"""

		if username != '':
			query = {'_id': username}
		elif email != '':
			query = {'account.email': email}
		else:
			raise Exception('need to supply either username or email, none were given')

		query['account.password'] = password  # add password part to query

		#put it in a temporary variable in case it is incorrect - shouldn't load the user until they are correctly logged in
		tmpUser = db.user.find_one(query)

		if tmpUser == None:  # means nothing was returned from mongo query
			raise Exception('incorrect info')  # maybe better to only say "incorrect info" to increase security

		self.data = tmpUser  # inputs are correct, put user object in correct place

		#CONSIDER: check if currently logged in and run logout if true?

		#zero out ip & token for users w/ same ip
		db.user.update(
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

		self.data['session']['token'] = str(uuid.uuid4())
		self.data['session']['ip'] = web.ctx.ip
		self.data['session']['startTime'] = time.time()

	def logout(self):
		"""logs out current user by removing ip & token from db"""
		return 'logout not finished'

	def can(self, action):
		"""determines if user has permission to do a particular action (returns true or false)"""
		return action in self.data['permission']

	def validateData(self):
		"""validates user.data - intended to be used for signup and user info changes to determine if user data is acceptable"""
		return 'validateData not finished'

	def save(self):
		"""
			update the representation of the user object in mongo - this is called at the end of the script
			consider switching to a transparent method of writing to the db
		"""
		if self.data['_id'] != 'guest':  # shouldn't save guest account to db because guest isn't a real user
			db.user.save(self.data)

"""
abc = user()
abc.data['permission'] = 'the stuff'
abc.data['account'] = {'pword': 'the stuff'}
print abc.data['account']['pword']
abc.data['account']['pword'] = 'fffdf'
print abc.data['account']['pword']
print abc.can('input')
"""
