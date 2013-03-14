########################################################
### Place to do match-based doc collection
### (Should collect every commit related to a certain match) (Useful for analysis)
########################################################

import model.commit
from werkzeug import exceptions as ex


class Match(object):
	def __init__(self, match_type, match_num):
		self.match_type = str(match_type)
		self.match_num = int(match_num)
		if not model.commit.find_one({'data.match_type': self.match_type, 'data.match_num': self.match_num}):
			raise ex.NotFound("No commits for match %s %s." % (self.match_type, self.match_num))

	def __iter__(self):
		return model.commit.find({'data.match_type': self.match_type, 'data.match_num': self.match_num})

	def teams(self):
		t = []
		for i in self:
			if i.data['team'] in t:
				continue
			else:
				t.append(i.data['team'])
				yield i.data['team']

	def __json__(self):
		return [i for i in self]
