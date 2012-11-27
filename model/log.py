from mongo_descriptors import Db, MongoI
from time import time


def error(*text):
	print ' '.join(text)
	Log('errors').append(text)


class Log(object):
	"""Represents a log document"""
	db = Db('log', root='csd')
	log = MongoI('entries', typ=list)
	raw = MongoI()

	def __init__(self, oi):
		if not self.db.find_one(self.oi):
			self.db.insert(
				{"_id": self.oi}
			)

	def append(self, *entries):
		logentry = (time(), ' '.join(entries))
		self.log += [logentry]


def defaults():
	Log('errors')
