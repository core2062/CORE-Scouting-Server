from datetime import datetime
import db
import event as event_scraper
import match as match_scraper
import team as team_scraper

"""
this script defines tasks such as scraping and analysis which are used to run the CSD
this is where DB interaction happens for these tasks
all event functions are called for a specific year to avoid rescraping past years which cannot logically change
"""


def event_names(year=datetime.now().year):
	"""
	this task scrapes event names and other basic info which is later used for getting more advanced event info
	it basically just prepares a document for scrape_event() to use and add data to
	we assume that all previous years have been scraped (however the db setup script can call this for previous years)
	this function will not overwrite entries that are already in the db, it only adds new ones (so other scraping functions can add data to the documents and it won't be lost)
	"""

	print 'getting event list'

	year = int(year)  # make sure it is an int

	event_list = event_scraper.get_event_list(year)

	for event in event_list:
		if db.csd.sourceEvent.find_one({'name': event['name'], 'year': year}) == None:
			event['year'] = year  # set year value
			db.csd.sourceEvent.save(event)


def event_details(year=datetime.now().year):
	"""
	this function uses data produced by event_names() to get more data about events which have been found
	it will change existing records to match the event data in the FIRST FMS (like if more teams register for an event), but should not change data created by event_names()
	this should be run more often than scrape_event_names() because events change details like attendance more often than they are created
	"""

	year = int(year)  # make sure it is an int

	event_list = db.csd.sourceEvent.find({'year': year})
	for event in event_list:
		print 'getting details on the ' + event['name']
		event.update(event_scraper.get_event(eid=event['eid'], year=event['year']))
		db.csd.sourceEvent.update({'_id': event['_id']}, event)


def all_matches(year=datetime.now().year):
	"""this function scrapes all matches for a entire year"""

	event_list = db.csd.sourceEvent.find({'year': year})
	for event in event_list:
		match(event['short_name'], year)


def match(event_short_name, year=datetime.now().year):
	"""
	this function uses data produced by event_details() to get matches from a event which has been scraped
	it will change existing match records to match the event data in the FIRST FMS, as matches occur
	this should be run often during a competition to get new match results
	"""

	year = int(year)  # make sure it is an int

	print 'getting matches from ' + event_short_name

	matches = match_scraper.get_matches(year, event_short_name)

	for match in matches:
		match['year'] = year  # add year to the match result
		match['event'] = event_short_name  # add event_short_name to the match result

		db.csd.sourceMatch.update(
			{
				'year': year,
				'comp_level': match['comp_level'],
				'set_number': match['set_number'],
				'match_number': match['match_number'],
				'event': event_short_name
			},
			match,
			upsert=True,
		)


def tpids(year=datetime.now().year):
	"""
	get tpids for all teams in a certain year
	this function adds tpid info to team objects
	"""
	print 'getting tpid list'

	year = int(year)  # make sure it is an int

	tpid_list = team_scraper.get_tpids(year)

	for tpid in tpid_list:
		db.csd.sourceTeam.update(
			{
				'team': tpid['team']
			},
			{
				'$set': {
					'tpid.' + str(year): tpid['tpid']
				}
			},
			upsert=True,
		)


def team_details():
	"""this code is written with the assumption that only the most recent info should be gotten about the teams"""

	for team in db.csd.sourceTeam.find({}):
		tpid = None
		year = datetime.now().year

		while tpid == None:  # loop till it finds the most recent tpid
			try:
				tpid = team['tpid'][str(year)]
			except:
				year += -1

		print 'scraping team %s with tpid from %s' % (team['team'], year)

		team.update(team_scraper.get_team_details(tpid, year))
		db.csd.sourceTeam.update({'_id': team['_id']}, team)
