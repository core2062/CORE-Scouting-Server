#from celery.decorators import task
from datetime import datetime
from model.db import database as db
import scraper.event

"""
	this script defines tasks such as scraping and analysis which are used to run the CSD
	here is where DB interaction happens for these tasks
"""


#@task
def scrape_event_names(year=datetime.now().year):
	"""
	this task scrapes event names and other basic info which is later used for
	getting more advanced event info we assume that all previous years have
	been scraped (however the db setup script can call this for previous
	years)
	"""

	event_list = scraper.event.getEventList(year)

	for event in event_list:
		if db.sourceEvent.find_one({'name': event['name'], 'year': year}) == None:

			#change name of key (better/shorter name)
			event['type'] = event['event_type']
			del event['event_type']

			#change name of key (better/shorter name)
			event['eid'] = event['first_eid']
			del event['first_eid']

			#set year value
			event['year'] = year

			db.sourceEvent.save(event)
