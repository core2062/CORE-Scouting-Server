from numpy.linalg import lstsq as least_squares
from model.db import database as db


def opr(entries):
	# build id map of unique teams
	team_id_map = []
	for entry in entries:
		for team in entry[1:]:
			if team not in team_id_map:
				team_id_map.append(team)

	# populate matrix
	total_teams = len(team_id_map)
	M = []  # a (2m x total_teams) matrix where m is # of matches
	s = []  # a (2m x 1) matrix
	for entry in entries:
		s.append(entry[0])  # add alliance score
		row = [0] * total_teams
		for team in entry[1:]:
			row[team_id_map.index(team)] = 1
		M.append(row)

	print M
	print s
	return dict(zip(team_id_map, least_squares(M, s)[0]))


def run_dat():
	entries = []
	for match in db.sourceMatch.find({'year':2013}):
		for color in ('red', 'blue'):
			entries.append((
				match['alliance'][color]['score'],
				match['alliance'][color]['teams'][0],
				match['alliance'][color]['teams'][1],
				match['alliance'][color]['teams'][2],
			))
	print entries
	print opr(entries)
