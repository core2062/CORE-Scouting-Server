from numpy.linalg import lstsq as least_squares


def opr(entries):
	"""
	This function creates a overdetermined linear system where each equation
	is an alliance in a match (so there are 2 equations per match). The
	equations are set equal to the alliance's score for that match. Then,
	using the least_squares method, the system is solved, giving an
	approximation of each team's contribution to the score of their alliances.

	entries is an array of tuples formatted like `(alliance_score, team_1,
	team_2, team_3)` - there are 2 tuples per match
	returns a dict formatted like `{"team_num": team_opr}`
	"""
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

	return dict(zip(team_id_map, least_squares(M, s)[0]))
