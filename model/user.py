class user:
	"""
		this class deals with all user data and authentication of the user
	"""

	def __getitem__(self, key):
		print '(get)', ' key:', key
		#return self.value

	def __setitem__(self, key, value):
		print '(set)', ' key:', key, ' value:', value
		#self.value = value

	def __delitem__(self, key):
		print '(delete)', ' key:', key
		#del self

	data = { #initialized with defaults (for guest user)
		'_id': 'guest',
		'account': {
			'pword': '',
			'email': '',
		},
		'permission': [ #list of permissions that user has
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
		'opt': { #optional info
			'zip': '',
			'browser': '',
			'gender': '',
		},
		'status': { #info about current session
			'ip': '',
			'logintime': '', #time when last logged in (when token was issued)
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

		#check permissions (not banned, which is no permissions)

		#consider using random id for normal usernames (login with only email) and special username for admin / guest
		return 'check not finished'

	def login(self, password, username='', email=''):
		"""
			checks username / email & password and if correct, generates token and puts user object in data
			used when user is not yet logged in (has no token)
			can login with either email or username
		"""
		return 'login not finished'

	def logout(self):
		"""logs out current user by removing ip & token from db"""
		return 'logout not finished'

	def can(self, action):
		"""determines if user has permission to do a particular action (returns true or false)"""
		return action in self.data['permission']

	def validateData(self):
		"""validates user.data - intended to be used for signup and user info changes to determine if user data is acceptable"""
		return 'validateData not finished'

abc = user()
abc['permission'] = 'the stuff'
abc['permission']['ff'] = 'the stuff'
print abc.can('input')
print abc
