from mongo_descriptors import Db, MongoI
from time import time
from functools import partial


def log(logt, *text):
	print "%s:  %s" % (logt, ' '.join(text))
	Log(logt).append(*text)


class Log(object):
	"""Represents a log document"""
	db = Db('log', root='csd')
	log = MongoI('entries', typ=list)
	raw = MongoI()

	def __init__(self, oi):
		self.oi = oi
		if not self.db.find_one(self.oi):
			self.db.insert(
				{"_id": self.oi}
			)

	def append(self, *entries):
		logentry = (time(), ' '.join(entries))
		self.log += [logentry]


error = partial(log, 'errors')
security = partial(log, 'security')


def defaults():
	Log('errors')
	Log('security')
