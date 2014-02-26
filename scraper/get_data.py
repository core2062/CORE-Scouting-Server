from datetime import datetime

from config import app
import scraper.event as event_scraper
import scraper.match as match_scraper
import scraper.team as team_scraper
import tba
from model.db import database as db
import os

"""
this script defines tasks such as scraping and analysis which are used to run
the CSD this is where DB interaction happens for these tasks all event
functions are called for a specific year to avoid rescraping past years which
cannot logically change
"""


def events(year=datetime.now().year):
	print 'getting event list for {}'.format(year)
	year = int(year)  # make sure it is an int
	for event in tba.events(year):
		db.fms.save(event)


def teams(year = datetime.now().year):
	print 'getting teamdata for {}'.format(year)
	year = int(year)
	for team in tba.teams(year):
		db.fms.save(team)

def match(event_key):
	event = db.fms.find_one(event_key)

# def all_matches(year=datetime.now().year):
# 	"""this function scrapes all matches for a entire year"""

# 	year = int(year)  # make sure it is an int

# 	# the parser for 2003/2004/2005 matches is not finished yet, remove this
# 	# when it is
# 	if year in (2003, 2004, 2005, 2006):
# 		print str(year) + " isn't done"
# 		return

# 	print 'getting all matches from ' + str(year)

# 	event_list = db.sourceEvent.find({'year': year})
# 	for event in event_list:
# 		if event['short_name'] != None:
# 			for short_name in event['short_name']:
# 				try:
# 					match(short_name, year)
# 				except Exception:
# 					print "error!"
# 		else:
# 			print '...no matches'


# def match(event_short_name, year=datetime.now().year):
# 	"""
# 	this function uses data produced by event_details() to get matches from a
# 	event which has been scraped it will change existing match records to
# 	match the event data in the FIRST FMS, as matches occur this should be run
# 	often during a competition to get new match results
# 	"""
# 	year = int(year)  # make sure it is an int
# 	print 'getting matches from ' + event_short_name
# 	matches = match_scraper.get_matches(year, event_short_name)

# 	for match in matches:
# 		match['year'] = year  # add year to the match result
# 		match['event'] = event_short_name  # add event_short_name to the match result

# 		db.sourceMatch.update(
# 			{
# 				'year': year,
# 				'comp_level': match['comp_level'],
# 				'set_number': match['set_number'],
# 				'match_number': match['match_number'],
# 				'event': event_short_name
# 			},
# 			match,
# 			upsert=True,
# 		)
