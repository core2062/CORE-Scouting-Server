from datetime import datetime
import db
import scraper.event

"""
	this script defines tasks such as scraping and analysis which are used to run the CSD
	this is where DB interaction happens for these tasks
	all event functions are called for a specific year to avoid rescraping past years which cannot logically change
"""


def scrape_event_names(year=datetime.now().year):
	"""
	this task scrapes event names and other basic info which is later used for getting more advanced event info
	it basically just prepares a document for scrape_event() to use and add data to
	we assume that all previous years have been scraped (however the db setup script can call this for previous years)
	this function will not overwrite entries that are already in the db, it only adds new ones (so other scraping functions can add data to the documents and it won't be lost)
	"""

	event_list = scraper.event.getEventList(year)

	for event in event_list:
		if db.csd.sourceEvent.find_one({'name': event['name'], 'year': year}) == None:

			#change name of key (better/shorter name)
			event['type'] = event['event_type']
			del event['event_type']

			#change name of key (better/shorter name)
			event['eid'] = event['first_eid']
			del event['first_eid']

			#set year value
			event['year'] = year

			db.csd.sourceEvent.save(event)


def scrape_event(year=datetime.now().year):
	"""
	this function uses data produced by scrape_event_names() to get more data about events which have been found
	it will change existing records if the event data in the FIRST FMS (like more teams regester for an event), but will not change data created by scrape_event_names()
	"""
