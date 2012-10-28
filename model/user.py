from mongo_descriptors import Db, MongoI
from os import urandom
from time import time

from passwords import pwd_context
from model.db import database as db
from config import ALLOW_TOKENS_TO_CHANGE_IP, TOKEN_LENGTH


def auth(name, password):
	user = db.user.find_one({"_id": str(name)})
	if not password:
		password = ""
	if not user:
		return None
	if pwd_context.verify(password, user["password"]):
		user = User(name)
		user.new_session()
		return user
	else:
		return False


def token_auth(token, ip=None):
	user = db.user.find_one({"token": str(token)})
	if not user:
		return None
	if ip and not ALLOW_TOKENS_TO_CHANGE_IP:
		if user.ip != ip:
			return False
	else:
		return User(user['_id'])


class User(object):
	db = Db(db=db['user'])
	fullname = MongoI("fullname", typ=str)
	password = MongoI("password")
	perms = MongoI("perms", typ=list)

	email = MongoI("email", typ=str)
	team = MongoI("team", typ=int)

	token = MongoI("token")
	ip = MongoI("ip")
	startTime = MongoI('startTime')

	raw = MongoI()

	def __init__(self, name, create=False):
		self.oi = str(name)
		if self.db.find_one(self.oi) == None:
			if create:
				self.db.insert({"_id": self.oi})
			else:
				raise ValueError("No user " + self.oi)

	def passwd(self, password):
		self.password = pwd_context.encrypt(password)

	def has_perm(self, perm):
		perm = str(perm)
		if "-" + perm in self.perms:
			return False
		if "*" in self.perms:
			return True
		return perm in self.perms

	def give_perm(self, perm):
		if not perm in self.perms:
			self.perms += [str(perm)]

	def new_session(self, ip):
		self.token = urandom(TOKEN_LENGTH).encode('base64')
		self.ip = ip
		self.startTime = time()

	def logout(self):
		self.token = None
		self.ip = None
		self.startTime = None

	def __repr__(self):
		return str(self.oi) + "(" + self.fullname + ")"

	def __json__(self):
		return {
			'name': self.oi,
			'fullname': self.fullname,
			'email': self.email,
			'team': self.team,
		}


def new_user(name, password, fullname=None, team=None, email=None):
	u = User(name, create=True)

	u.passwd(password)
	if fullname:
		u.fullname = fullname
	if email:
		u.email = email
	if team:
		u.team = team
	return u


def defaults():
	u = new_user("admin", 'mApru', fullname='Kai\'ckul')
	u.give_perm("*")
	u = new_user('test-user', 'm3jhrk4')


def list_users():
	users = db.user.find()
	ret = []
	for i in users:
		ret.append(User(i["_id"]))
	return ret
