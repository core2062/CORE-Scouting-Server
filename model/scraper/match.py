import urllib2
from BeautifulSoup import BeautifulSoup, NavigableString

"""
Facilitates grabbing Match information from USFIRST.org. It enables discovering matches from official FIRST events
It returns Match model objects, but does no database IO itself.
"""

EVENT_SHORT_EXCEPTIONS = {
	"arc": "Archimedes",
	"cur": "Curie",
	"gal": "Galileo",
	"new": "Newton",
}

MATCH_RESULTS_URL_PATTERN = "http://www2.usfirst.org/%scomp/events/%s/matchresults.html"  # % (year, event_short)
MATCH_SCHEDULE_QUAL_URL_PATTERN = "http://www2.usfirst.org/%scomp/events/%s/schedulequal.html"
MATCH_SCHEDULE_ELIMS_URL_PATTERN = "http://www2.usfirst.org/%scomp/events/%s/scheduleelim.html"


def get_matches(year, event_short_name):
	"""Return a list of Matches based on the FIRST match results page"""

	url = MATCH_RESULTS_URL_PATTERN % (year, EVENT_SHORT_EXCEPTIONS.get(event_short_name, event_short_name))

	try:
		result = urllib2.urlopen(url, timeout=60)
	except urllib2.URLError, e:  # raise a better error
		raise Exception('unable to retrieve url (for session key): ' + url + ' reason:' + str(e.reason))

	return parse_match_results_list(result.read())


def parse_match_results_list(html):
	"""Parse the match results from USFIRST. This provides us with information about Matches and the teams that played in them"""

	matches = []

	soup = BeautifulSoup(
		html,
		convertEntities=BeautifulSoup.HTML_ENTITIES
	)

	tables = soup.findAll('table')

	matches.extend(parse_match_result(tables[2]))
	matches.extend(parse_match_result(tables[3]))
	return matches


def parse_match_result(table):
	"""Parse the table that contains match results"""

	matches = []

	for tr in table.findAll('tr')[3:]:
		tds = tr.findAll('td')
		if len(tds) == 11 and _recurse_until_string(tds[1]) is not None:
			if _recurse_until_string(tds[1]) is not None:
				match_number_info = parse_elim_match_number(_recurse_until_string(tds[1]))
				del tds[1]  # table is now the same as for a qualification match

				comp_level = match_number_info["comp_level"]
				set_number = match_number_info["set_number"]
				match_number = match_number_info["match_number"]

		elif len(tds) == 10 and _recurse_until_string(tds[1]) is not None:

			comp_level = "qm"
			set_number = None
			match_number = int(_recurse_until_string(tds[1]))

		else:
			raise Exception('incorrect table length or some other messed up input')

		red_teams = [int(_recurse_until_string(tds[2])), int(_recurse_until_string(tds[3])), int(_recurse_until_string(tds[4]))]
		blue_teams = [int(_recurse_until_string(tds[5])), int(_recurse_until_string(tds[6])), int(_recurse_until_string(tds[7]))]

		if tds[8].string == None:
			red_score = -1
		else:
			red_score = int(_recurse_until_string(tds[8]))

		if tds[9].string == None:
			blue_score = -1
		else:
			blue_score = int(_recurse_until_string(tds[9]))

		match = {
			'comp_level': comp_level,
			'set_number': set_number,
			'match_number': match_number,
			'alliance': {
				"red": {
					"teams": red_teams,
					"score": red_score,
				},
				"blue": {
					"teams": blue_teams,
					"score": blue_score,
				},
			},
		}

		# Don't write down uncompleted matches
		# NOTICE: if FIRST decides to make a game w/ negitive scores then this code will have to be redone
		if (red_score > -1 and blue_score > -1):
			matches.append(match)

		# except Exception, detail:
		# 	raise Exception('Match Parse Failed: ' + str(detail))

	return matches


def parse_elim_match_number(string):
	"""
	Parse out the information about an elimination match based on the string USFIRST provides.
	They look like "Semi 2-2"
	"""

	comp_level_dict = {
		"Qtr": "qf",
		"Semi": "sf",
		"Final": "f",
	}

	#string comes in as unicode.
	string = str(string)
	string = string.strip()

	match_number = int(string[-1:])
	set_number = int(string[-3:-2])
	comp_level = comp_level_dict[string[:-4]]

	results = {
		"match_number": match_number,
		"set_number": set_number,
		"comp_level": comp_level,
	}

	return results


def _recurse_until_string(node):
	"""
	Digs through HTML that MS Word made worse.
	Written to deal with http://www2.usfirst.org/2011comp/Events/cmp/matchresults.html
	"""
	if node.string is not None:
		return node.string
	if isinstance(node, NavigableString):
		return node
	if hasattr(node, 'contents'):
		for content in node.contents:
			result = _recurse_until_string(content)
			result = result.strip().replace('\r', '').replace('\n', '').replace('  ', ' ')
			if result is not None and result != "":
				return result
	return None
