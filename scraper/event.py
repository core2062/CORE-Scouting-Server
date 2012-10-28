from datetime import datetime
from calendar import timegm
from BeautifulSoup import BeautifulSoup
import re
import helper

"""
this script provides functions to scrape the FIRST FMS database
all functions in this script are database independent, database-dependent functions are in scraper.py
"""

# The types of events listed in the event list:
REGIONAL_EVENT_TYPES = [
	"Championship",
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


# def scrape_duration(start_date, end_date):
# 	"""scrape all the events that started within a specified duration"""


def get_event_list(year):
	"""
	get a list of Event objects from the FIRST event listing page and parse the list of events
	This provides us with basic information about events and is how we first discover them.
	returns back a list of dictionaries.

	if there are more than 250 events then this function will break because the site splits the return into pages w/ 250 on each page
	"""

	html = helper.url_fetch(REGIONAL_EVENTS_URL % year)

	soup = BeautifulSoup(
		html,
		convertEntities=BeautifulSoup.HTML_ENTITIES
	)

	events = []
	content = soup.p.table.table.findAll('tr')[3:-2]  # get to the actual content, past all the shitty layout tables and headers / footers

	for tr in content:
		event = {}

		tds = tr.findAll('td')
		event["type"] = unicode(tds[0].string)
		event["eid"] = int(tds[1].a["href"][24:28])
		event["name"] = ''.join(tds[1].a.findAll(text=True))  # <em>s in event names fix

		if event["type"] in REGIONAL_EVENT_TYPES:  # actually this url shouldn't return kickoffs anyway, probably not needed
			events.append(event)

	return events


def get_event(year, eid):
	"""populate an event object with other data form different parts of the FIRST FMS DB, including event registration"""

	session_key = helper.get_session_key(year)
	event = parse_event(helper.url_fetch(EVENT_URL_PATTERN % (eid, session_key)))
	event['official'] = True  # wtf is this???
	event['teams'] = get_event_registration(eid, year)

	return event

# it used to be called "matchsum" in 2003 and "matches" in 2004
EVENT_SHORT_NAME_RE = re.compile(r"http://www2\.usfirst\.org/[0-9]*comp/Events/([a-zA-Z0-9]*)/match(:?results|sum|es)\.html")


def parse_event(html):
	"""
	Parse an event's specific page HTML from FIRST into the individual
	fields of an Event object. This updates events and gets us fuller
	information once we know about this.
	"""

	event_dict = {}
	soup = BeautifulSoup(
		html,
		convertEntities=BeautifulSoup.HTML_ENTITIES,
	)

	for tr in soup.findAll('tr'):
		tds = tr.findAll('td')
		if len(tds) > 1:
			field = str(tds[0].string)

#			if field == "Event":
#				event_dict["name"] = unicode(''.join(tds[1].findAll(text=True))).strip()
			if field == "Event Subtype":
				event_dict["type"] = unicode(tds[1].string)
			elif field == "When":
				event_dates = str(tds[1].string).strip()
				event_dict["start_date"], event_dict["end_date"] = parse_event_dates(event_dates)
				event_dict["year"] = int(event_dates[-4:])

			elif field == "Where":
				# TODO: This next line is awful. Make this suck less.
				# I think \t tabs mess it up or something. -greg 5/20/2010
				event_dict["venue_address"] = unicode(''.join(tds[1].findAll(text=True))).encode('ascii', 'ignore').strip().replace("\t", "").replace("\r\n\r\n", "\r\n")
			elif field == "Event Info":
				event_dict["website"] = unicode(tds[1].a['href'])
			elif field == "Match Results":
				#example: http://www2.usfirst.org/2010comp/Events/SDC/matchresults.html
				event_dict["short_name"] = []  # championship events have multiple short_names (1 for each division)

				standings_links = tds[1].findAll('a')
				for link in standings_links:
					event_dict["short_name"].append(re.match(EVENT_SHORT_NAME_RE, link["href"]).group(1).lower())  # lowercase just looks nicer and more consistant

	event = {
		'short_name': event_dict.get("short_name", None),
		'type': event_dict.get("type", None),
		'start_date': event_dict.get("start_date", None),
		'end_date': event_dict.get("end_date", None),
		'venue_address': event_dict.get("venue_address", None),
		'website': event_dict.get("website", None),
	}

	return event


def parse_event_dates(datestring):
	"""
		Parses the date string provided by First into actual event start and stop DateTimes and then outputs as unix timestamps
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

	start_day = int(datestring[0:2])
	start_month = month_dict[datestring[3:6]]
	start_year = int(datestring[-4:])

	if len(datestring) == 11:  # check if the date string only gives one date like 09-Mar-2005 (assume one day event?)
		#make stop date the same as start
		stop_day = start_day
		stop_month = start_month
		stop_year = start_month
	else:  # regular 2 part date string
		stop_day = int(datestring[9:11])
		stop_month = month_dict[datestring[12:15]]
		stop_year = start_year  # there are no events near new-years and datestrings only give one year

	start_date = datetime(start_year, start_month, start_day)
	stop_date = datetime(stop_year, stop_month, stop_day)

	return (timegm(start_date.utctimetuple()), timegm(stop_date.utctimetuple()))


def get_event_registration(eid, year):
	"""Returns a list of team_numbers attending a particular Event"""

	session_key = helper.get_session_key(year)
	teams = parse_event_registration(helper.url_fetch(EVENT_REGISTRATION_URL_PATTERN % (eid, session_key)))
	return teams


def parse_event_registration(html):
	"""Find what Teams are attending an Event, and return their team_numbers."""

	# This code is based on TeamTpidHelper, and should probably be refactored.
	# -gregmarra 5 Dec 2010

	teamRe = re.compile(r'tpid=[A-Za-z0-9=&;\-:]*?">\d+')
	teamNumberRe = re.compile(r'\d+$')

	teams = []
	for teamResult in teamRe.findall(html):
		teams.append(teamNumberRe.findall(teamResult)[0])  # add team to list

	return teams
