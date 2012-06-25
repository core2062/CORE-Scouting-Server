from datetime import datetime
from BeautifulSoup import BeautifulSoup
import re
import urllib2

"""
this script provides functions to scrape the FIRST FMS database
all functions in this script are database independent, database-dependent functions are in scraper.py
"""

# The types of events listed in the event list:
REGIONAL_EVENT_TYPES = [
	"Regional",
	"MI FRC State Championship",
	"MI District",
	"Qualifying Event",
	"Qualifying Championship",
	"District Event",
	"District Championship",
]

# The URL for the event list:
REGIONAL_EVENTS_URL = "https://my.usfirst.org/myarea/index.lasso?event_type=FRC&season_FRC=%s"

# The URL pattern for specific event pages, based on their USFIRST event id.
EVENT_URL_PATTERN = "https://my.usfirst.org/myarea/index.lasso?page=event_details&eid=%s&-session=myarea:%s"

# The URL pattern for team registration information, based on USFIRST event id.
EVENT_REGISTRATION_URL_PATTERN = "https://my.usfirst.org/myarea/index.lasso?page=event_teamlist&results_size=250&eid=%s&-session=myarea:%s"


# MASSIVE FIXME:
# Just discovered that FIRST session keys are season-dependent. A session key you retrieved from a 2011
# page does not work to get information about 2012 events. Therefore every request must also know what year
# it is for. Have not fully made changes to be aware of this, as it ripples very far downstream in terms of
# changing the API to require (eid, year) and not just eid. Right now, this means updating data on any event
# prior to 2012 will fail. Need to ripple these changes through everything that gets data from my.usfirst.org
#
# Every function call with year=2012 should change to year required.
#
# -gregmarra 15 Jan 2012


# def scrape_duration(start_date, end_date):
# 	"""scrape all the events that started within a specified duration"""


# a URL that gives us a result with urls that have session keys in them (response only shows 25 results from FMS DB... pretty small request)
SESSION_KEY_GENERATING_PATTERN = "https://my.usfirst.org/myarea/index.lasso?page=searchresults&programs=FRC&reports=teams&omit_searchform=1&season_FRC=%s"


def get_session_key(year):
	"""
	Grab a page from FIRST so we can get a session key out of URLs on it.
	This session key is needed to construct working event detail information URLs.
	"""
	sessionRe = re.compile(r'myarea:([A-Za-z0-9]*)')
	url = SESSION_KEY_GENERATING_PATTERN % year

	try:
		result = urllib2.urlopen(url, timeout=60)
	except urllib2.URLError, e:  # raise a better error
		raise Exception('unable to retrieve url (for session key): ' + url + ' reason:' + str(e.reason))

	regex_results = re.search(sessionRe, result.read())
	if regex_results is not None:
		session_key = regex_results.group(1)  # first parenthetical group
		if session_key is not None:
			return session_key

	#else: (if above didn't return)
	raise Exception('unable to extract session key from result')


def get_event_list(year):
	"""
	get a list of Event objects from the FIRST event listing page and parse the list of events
	This provides us with basic information about events and is how we first discover them.
	returns back a list of dictionaries.

	if there are more than 250 events then this function will break because the site splits the return into pages w/ 250 on each page
	"""
	url = REGIONAL_EVENTS_URL % year

	try:
		result = urllib2.urlopen(url, timeout=60)
	except urllib2.URLError, e:
		raise Exception('Unable to retrieve url: ' + url + ' Reason:' + e.reason)
		return

	html = result.read()

	events = []
	soup = BeautifulSoup(
		html,
		convertEntities=BeautifulSoup.HTML_ENTITIES
	)

	content = soup.p.table.table.findAll('tr')[3:-2]  # get to the actual content, past all the shitty layout tables and headers / footers

	for tr in content:
		event = {}

		tds = tr.findAll('td')
		event["event_type"] = unicode(tds[0].string)
		event["first_eid"] = tds[1].a["href"][24:28]
		event["name"] = ''.join(tds[1].a.findAll(text=True))  # <em>s in event names fix

		if event.get("event_type", None) in REGIONAL_EVENT_TYPES:  # actually this url shouldn't return kickoffs anyway, probably not needed
			events.append(event)

	return events


def get_event(year, eid):
	"""populate an event object with other data form different parts of the FIRST FMS DB, including event registration"""

	session_key = get_session_key(year)
	url = EVENT_URL_PATTERN % (eid, session_key)

	try:
		result = urllib2.urlopen(url, timeout=60)
	except urllib2.URLError, e:
		raise Exception('Unable to retrieve url: ' + url + ' Reason:' + e.reason)

	event = parse_event(result.read())
	event['official'] = True  # wtf is this???
	event['teams'] = get_event_registration(eid, year)
	return event


def parse_event(html):
	"""
	Parse an event's specific page HTML from USFIRST into the individual
	fields of an Event object. This updates events and gets us fuller
	information once we know about this.
	"""
	event_dict = dict()
	soup = BeautifulSoup(html,
			convertEntities=BeautifulSoup.HTML_ENTITIES)

	for tr in soup.findAll('tr'):
		tds = tr.findAll('td')
		if len(tds) > 1:
			field = str(tds[0].string)
			if field == "Event":
				event_dict["name"] = unicode(''.join(tds[1].findAll(text=True))).strip()
			if field == "Event Subtype":
				event_dict["type"] = unicode(tds[1].string)
			if field == "When":
				try:
					event_dates = str(tds[1].string).strip()
					event_dict["start_date"], event_dict["end_date"] = parse_event_dates(event_dates)
					event_dict["year"] = int(event_dates[-4:])
				except Exception, detail:
					raise Exception('Date Parse Failed: ' + str(detail))
			if field == "Where":
				# TODO: This next line is awful. Make this suck less.
				# I think \t tabs mess it up or something. -greg 5/20/2010
				event_dict["venue_address"] = unicode(''.join(tds[1].findAll(text=True))).encode('ascii', 'ignore').strip().replace("\t", "").replace("\r\n\r\n", "\r\n")
			if field == "Event Info":
				event_dict["website"] = unicode(tds[1].a['href'])
			if field == "Match Results":
				#http://www2.usfirst.org/2010comp/Events/SDC/matchresults.html
				m = re.match(r"http://www2\.usfirst\.org/%scomp/Events/([a-zA-Z0-9]*)/matchresults\.html" % event_dict["year"], tds[1].a["href"])
				event_dict["short_name"] = m.group(1).lower()

	event = {
		'name': event_dict.get("name", None),
		'type': event_dict.get("type", None),
		'start_date': event_dict.get("start_date", None),
		'end_date': event_dict.get("end_date", None),
		'venue_address': event_dict.get("venue_address", None),
		'website': event_dict.get("website", None),
		'short_name': event_dict.get("event_short", None)
	}

	return event


def parse_event_dates(datestring):
	"""
		Parses the date string provided by USFirst into actual event start and stop DateTimes.
		FIRST date strings look like "01-Apr - 03-Apr-2010".
	"""
	month_dict = {
		"Jan": 1,
		"Feb": 2,
		"Mar": 3,
		"Apr": 4,
		"May": 5,
		"Jun": 6,
		"Jul": 7,
		"Aug": 8,
		"Sep": 9,
		"Oct": 10,
		"Nov": 11,
		"Dec": 12,
	}

	# "01-Apr - 03-Apr-2010"
	start_day = int(datestring[0:2])
	start_month = month_dict[datestring[3:6]]
	start_year = int(datestring[-4:])

	stop_day = int(datestring[9:11])
	stop_month = month_dict[datestring[12:15]]
	stop_year = int(datestring[-4:])

	start_date = datetime(start_year, start_month, start_day)
	stop_date = datetime(stop_year, stop_month, stop_day)

	return (start_date, stop_date)


def get_event_registration(eid, year):
	"""Returns a list of team_numbers attending a particular Event"""

	session_key = get_session_key(year)
	url = EVENT_REGISTRATION_URL_PATTERN % (eid, session_key)

	try:
		result = urllib2.urlopen(url, timeout=60)
	except urllib2.URLError, e:
		raise Exception('Unable to retrieve url: ' + url + ' Reason:' + e.reason)

	teams = parse_event_registration(result.read())
	return teams


def parse_event_registration(html):
	"""Find what Teams are attending an Event, and return their team_numbers."""

	# This code is based on TeamTpidHelper, and show probably be refactored.
	# -gregmarra 5 Dec 2010

	teamRe = re.compile(r'tpid=[A-Za-z0-9=&;\-:]*?">\d+')
	teamNumberRe = re.compile(r'\d+$')
	tpidRe = re.compile(r'\d+')

	teams = []
	for teamResult in teamRe.findall(html):
		team = {}
		team["number"] = teamNumberRe.findall(teamResult)[0]
		team["tpid"] = tpidRe.findall(teamResult)[0]
		teams.append(team)

	return teams
