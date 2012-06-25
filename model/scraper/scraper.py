from datetime import datetime
import db
import model.scraper.event as event_scraper

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

	event_list = event_scraper.get_event_list(year)

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


def scrape_events(year=datetime.now().year):
	"""
	this function uses data produced by scrape_event_names() to get more data about events which have been found
	it will change existing records if the event data in the FIRST FMS (like more teams register for an event), but should not change data created by scrape_event_names()
	this should be run more often than scrape_event_names() because events change details like attendance more often than they are created
	"""

	event_list = db.csd.sourceEvent.find({'year': year})
	for event in event_list:
		event.update(event_scraper.get_event(eid=event['eid'], year=event['year']))
		db.csd.sourceEvent.update({'_id': event['_id']}, event)

	return 'done'
