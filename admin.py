import argparse
import sys

import model.user
import model.log
from model.db import clear as clear_db
from scraper import scraper
from config import CURRENT_EVENT


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


def scrape():
	#scraper.event_names()
	#scraper.event_details()
	#scraper.tpids()
	#scraper.team_details()
	scraper.match(CURRENT_EVENT)
	print "it worked!"

parser = argparse.ArgumentParser(description="A backend admin CLI to the CORE Scouting Database")
parser.add_argument('command')
args = parser.parse_args()
commands = {
	'list_users': list_users,
	'add_user': add_user,
	'defaults': defaults,
	'clear_db': clear_db,
}


commands[args.command]()
