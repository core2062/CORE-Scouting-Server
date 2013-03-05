#from datetime import datetime
import argparse
import sys

from main import app
import model.user
import model.log
import model.db
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
	scraper.all_matches(2011)

	#for year in range(STARTING_YEAR, CURRENT_YEAR + 1):
	#	scraper.event_names(year)
	#	scraper.event_details(year)
	#	scraper.tpids(year)


def scrape_teams():
	scraper.team_details()


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
}


commands[args.command]()
