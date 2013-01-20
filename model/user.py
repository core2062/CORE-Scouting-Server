from os import urandom
from time import time
from passlib.context import CryptContext
import collections

from model.db import database as db
from config import ALLOW_TOKENS_TO_CHANGE_IP, TOKEN_LENGTH

pwd_context = CryptContext(
	schemes=["sha512_crypt"],
	default="sha512_crypt",
	all__vary_rounds=0.1
)

# attributes of the user object that can be sent to the client. this doesn't
# currently support nested objects being included / excluded only entire
# properties
PUBLIC_ATTRS = ['prefs', 'email', 'team', 'name', 'token', 'permissions']

# attributes that the user can change
MUTABLE_ATTRS = ['prefs', 'email', 'team', 'name', 'password']


def password_auth(email, password="", ip=None):
	user_data = db.user.find_one({"email": email})
	if not user_data:
		return None
	if pwd_context.verify(password, user_data["password"]):
		user = User(user_data)
		user.new_session(ip)
		return user
	else:
		return False


def token_auth(token, ip=None):
	user_data = db.user.find_one({"token": str(token)})
	if not user_data:
		return None
	if ip and not ALLOW_TOKENS_TO_CHANGE_IP and user_data.ip != ip:
		# NOTE: if ip is not provided then ALLOW_TOKENS_TO_CHANGE_IP is
		# automatically not enforced
		return False
	else:
		return User(user_data)


class User(collections.Mapping):
	def __init__(self, *args, **kwargs):
		self.doc = dict(*args, **kwargs)

	def __getitem__(self, key):
		return self.doc[key]

	def __iter__(self):
		return iter(self.doc)

	def __len__(self):
		return len(self.doc)

	def __hash__(self):
		return hash(self.doc)

	def password(self, password):
		self.password = pwd_context.encrypt(password)

	def can(self, action):
		if "*" in self.doc['permissions']:
			return True
		return action in self.doc['permissions']

	def new_session(self, ip):
		# current session should be closed first
		self.logout()
		self.doc['token'] = urandom(TOKEN_LENGTH).encode('base64')
		self.doc['ip'] = ip
		self.doc['start_time'] = time()
		self.save()

	def logout(self):
		#move old session into log?
		self.doc['token'] = None
		self.doc['ip'] = None
		self.doc['start_time'] = None

	def update(self, data):
		# check data against the user_update schema
		for attr in MUTABLE_ATTRS:
			if attr in data.keys():
				if attr is 'password':
					self.password(data['password'])
				else:
					self.doc[attr] = data[attr]

	def save(self):
		db.user.save(self.doc)

	def __repr__(self):
		return str(self.doc['_id']) + "(" + self.doc['name'] + ")"

	def __json__(self):
		ret = {}
		for attr in PUBLIC_ATTRS:
			ret[attr] = self.doc[attr]
		return ret


def new_user(user_data):
	# email and password must be provided on signup
	if not ('email' in user_data.keys() and 'password' in user_data.keys()):
		raise ValueError('email and password are both required for signup')

	user = User()
	user.update(user_data)
	user.permissions = []  # default permissions
	return user


def list_users():
	users = db.user.find()
	ret = []
	for user_data in users:
		ret += repr(User(user_data))
	return ret
