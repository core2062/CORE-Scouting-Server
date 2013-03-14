#from datetime import datetime
import argparse
import sys

from config import app
import model.user
import model.log
import model.db
from model.db import database as db
import scraper.get_data as scraper


def add_user():
	name = raw_input("name> ")
	email = raw_input("email (optional)> ")

	def get_pw():
		password = raw_input("password> ")
		check_pw = raw_input("confirm> ")
		if check_pw != password:
			x = raw_input("Passwords do not match. Try again? (Y/n)")
			if x == "n":
				sys.exit()
			return get_pw()
		return password
	password = get_pw()
	model.user.new_user(name, password, email=email)


def defaults():
	model.user.defaults()
	model.log.defaults()


def list_users():
	for i in model.user.list_users():
		print i.oi, " (", i.fullname if i.fullname else "", ")"
		for key, value in i.raw.items():
			print "  ", key, ": ", value


def scrape_current():
	scraper.match(app.config["CURRENT_EVENT"])
	print "it worked!"


def scrape():
	# the FIRST FMS database only lists events back till 2003
	#STARTING_YEAR = 2011
	#CURRENT_YEAR = datetime.now().year
	scraper.all_matches(2013)

	#for year in range(STARTING_YEAR, CURRENT_YEAR + 1):
	#	scraper.event_names(year)
	#	scraper.event_details(year)
	#	scraper.tpids(year)


def scrape_teams():
	scraper.team_details()


def fix_team_num():
	current_event = db.sourceEvent.find_one({'short_name': ['mndu'], 'year': 2013})
	for entry in db.scouting.find():
		if not str(entry['team']) in current_event['teams']:
			print str(entry['team']) + " in match " + str(entry["match_num"]) + ' does not exist at this event '
			entry['team'] = raw_input("What is the real team number (\"idk\" to skip)? ")
			if not entry['team'] == 'idk':
				entry['team'] = int(entry['team'])
				db.scouting.update({"_id": entry['_id']}, entry)
				print 'fixed dat'
			else:
				print 'skipped dat shit, bro'


def find_double():
	for entry in db.scouting.find():
		#finds exact duplicates, deletes all but one
		del entry['_id']
		twins = db.scouting.find(entry)
		new_twins = []
		for brotha in twins:
			new_twins += [brotha]
		if len(new_twins) > 1:
			del new_twins[0]
			for brotha in new_twins:
				print 'killin\' dat brotha'
				db.scouting.remove(brotha)
			print 'removed: ' + str(len(new_twins))


def check_matches():
	#count teams per match
	#check for multiples of one team per match
	#notifies user, does not take action
	for match_type in ('q'):  # ('p', 'q', 'qf', 'sf', 'f'):
		for match_num in range(1, 100):
			total_entries = len(list(db.scouting.find({'match_num': match_num, 'match_type': match_type})))
			if not total_entries == 6 and not total_entries == 0:
				print "oh damn, %s has %s entr(y|ies)" % (match_num, total_entries)

	for entry in db.scouting.find():
		if entry['match_num'] > 90:
			print 'match ', entry['match_num'], 'looks wrong'


def validate():
	"""run various validation methods (all at once, in the most efficient order possible)"""
	find_double()
	fix_team_num()
	check_matches()


parser = argparse.ArgumentParser(description="A backend admin CLI to the CORE Scouting Database")
parser.add_argument('command')
args = parser.parse_args()
commands = {
	'list_users': list_users,
	'add_user': add_user,
	'defaults': defaults,
	'scrape': scrape,
	'scrape_current': scrape_current,
	'missing_team_list': scraper.get_missing_teams,
	'clear_db': model.db.clear,
	'backup': model.db.backup,
	'validate': validate,
}


commands[args.command]()
