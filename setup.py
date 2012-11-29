import model.db as db
from datetime import datetime

# TODO: switch to tasks to distribute load
import model.scraper.scraper as scraper


def setup():
	"""
		THIS FUNCTION IS NOT USED, AND WON"T BE USED ... IT IS FOR TESTING
		ONLY this function runs setup for the db and runs the scraper to get
		history for past years. don't call this if the db is already
		running... it will reset the db entirely
	"""

	db.reset()  # setup mongo

	#scraping setup

	CURRENT_YEAR = datetime.now().year

	# the FIRST FMS database only lists events back till 2003
	STARTING_YEAR = 2003

	for year in range(STARTING_YEAR, CURRENT_YEAR + 1):
		scraper.event_names(year)
		scraper.event_details(year)
		scraper.all_matches(year)
		scraper.tpids(year)

	scraper.team_details()
