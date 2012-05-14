import pymongo
import uuid

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
		'status': {  # info about current session
			'ip': '',
			'logintime': '',  # time when last logged in (when token was issued)
			'token': '',
		},
	}

	def check(self, token, username=''):
		"""
			checks username & token and if correct, puts the user object in data
			used to authenticate user is already logged in (has a token)
		"""
		#check token

		#check ip

		#consider using random id for normal usernames (login with only email) and special username for admin / guest
		return 'check not finished'

	def login(self, password, username='', email=''):
		"""
			checks username / email & password and if correct, generates token and puts user object in data
			used when user is not yet logged in (has no token)
			can login with either email or username
		"""

		if username != '':
			query = {'_id': username}
		elif email != '':
			query = {'account.email': email}
		else:
			raise Exception('need to supply either username or email, none were given')

		#put it in a temporary variable in case it is incorrect - shouldn't load the user until they are correctly logged in
		tmpUser = db.user.find_one(query)

		if tmpUser == None:  # means nothing was returned from mongo query
			raise Exception('incorrect username')  # maybe better to only say "incorrect info" to increase security

		if tmpUser['account']['password'] != password:
			raise Exception('incorrect password')  # maybe better to only say "incorrect info" to increase security

		self.data = tmpUser  # inputs are correct, put user object in correct place

		self.data.token = uuid.uuid4()

		print 'login not finished'

	def logout(self):
		"""logs out current user by removing ip & token from db"""
		return 'logout not finished'

	def can(self, action):
		"""determines if user has permission to do a particular action (returns true or false)"""
		return action in self.data['permission']

	def validateData(self):
		"""validates user.data - intended to be used for signup and user info changes to determine if user data is acceptable"""
		return 'validateData not finished'

"""
abc = user()
abc.data['permission'] = 'the stuff'
abc.data['account'] = {'pword': 'the stuff'}
print abc.data['account']['pword']
abc.data['account']['pword'] = 'fffdf'
print abc.data['account']['pword']
print abc.can('input')
"""
