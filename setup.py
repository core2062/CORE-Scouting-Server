import db
import task.task as task
from datetime import datetime

"""
	this script runs setup for the db and runs the scraper to get history for past years
	don't call this if the db is already running... it will reset the db entirely
"""

db.reset()  # setup mongo


#scraping setup

CURRENT_YEAR = datetime.now().year
STARTING_YEAR = 2003  # the FIRST FMS database only lists events back till 2003


def scrape_year(year):
	"""scrape everything from a year"""
	task.scrape_event_names(year)
