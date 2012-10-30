from mongo_descriptors import Db, MongoI
from time import time

def error(*text):
	print ' '.join(text)
	Log('errors').append(text*)

class Log(object):
	"""Represents a log document"""
	db = Db('log', root='csd')
	log = MongoI('entries',typ=list)
	raw = MongoI()
	def __init__(s, oi):
		s.oi = oi
		if s.db.find_one(oi)==None:
			s.db.insert({"_id":oi})
	def append(s,*entries):
		logentry = (time(),' '.join(entries))
		s.log+=[logentry]