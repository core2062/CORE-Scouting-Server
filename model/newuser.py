import pymongo
from passwords import pwd_context
from mongo_descriptors import Db, MongoI
from model.db import database as db
from config import ALLOW_TOKENS_TO_CHANGE_IP, TOKEN_LENGTH
from os import urandom

def auth(name, password):
	user = db.user.find_one({"_id" : str(name)})
	if not password:
		password = ""
	if not user:
		return None
	if pwd_context.verify(password, user["password"]):
		user = User(name)
		user.newSession()
		return user
	else:
		return False

def token_auth(token, ip=None):
	user = db.user.find_one({"token" : str(token)})
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

	def __init__(s, name, create=False):
		s.oi = str(name)
		if s.db.find_one(s.oi)==None:
			if create:
				s.db.insert({"_id":s.oi})
			else:
				raise ValueError("No user "+s.oi)

	def passwd(s, password):
		s.password = pwd_context.encrypt(password)

	def has_perm(s, perm):
		perm = str(perm)
		if "-"+perm in s.perms:
			return False
		if "*" in s.perms:
			return True
		return perms in s.perms

	def give_perm(s, perm):
		if not perm in s.perms:
			s.perms+=[str(perm)]

	def newSession(s,ip):
		s.token = urandom(TOKEN_LENGTH).encode('base64')
		s.ip = ip
		s.startTime = time()

	def logout(s):
		s.token = None
		s.ip = None
		s.startTime = None

	def __repr__(s):
		return str(s.oi) +" ("+ s.fullname +")"

	def __json__(s):
		return {'name':s.oi,'fullname':s.fullname,'email':s.email,'team':s.team}

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
	u = new_user('test-user','m3jhrk4')

def list_users():
	users = db.user.find()
	ret = []
	for i in users:
		ret.append(User(i["_id"]))
	return ret