#from datetime import datetime
import argparse
import sys

from config import app
import model.user
import model.log
import model.db
from model.db import database as db
import scraper.get_data as scraper
import analysis.opr


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

def scrape_events():
	scraper.events()

def scrape_teams():
	scraper.teams()

def fix_team_num():
	raise Exception("Needs to be updated for new db")
	current_event = db.sourceEvent.find_one({'short_name': ['wimi'], 'year': 2013})
	for entry in db.scouting.find():
		if not str(entry['team']) in current_event['teams']:
			print str(entry['team']) + " in match " + str(entry["match_num"]) + ' does not exist at this event '
			entry['team'] = raw_input("What is the real team number (\"next\" to skip)? ")
			if not entry['team'] == 'next':
				entry['team'] = int(entry['team'])
				db.scouting.update({"_id": entry['_id']}, entry)
				print 'fixed'
			else:
				print 'skipped'

def remove_duplicates():
	for entry in db.scouting.find():
		#finds exact duplicates, deletes all but one
		del entry['_id']  # ids are always unique
		entries = list(db.scouting.find(entry))

		# there should be one in the list, so remove it from the list of
		# entries to be deleted
		del entries[0]
		if len(entries) > 0:
			print 'removed: %s duplicate entry from match %s%s' % (len(entries), entry['match_type'], entry['match_num'])
			for entry in entries:
				db.scouting.remove(entry)


def check_matches():
	"""
	insure there are 6 entries per match
	insure all teams in a match are unique
	notifies user but doesn't take action
	"""

	for match_type in ('p', 'q', 'qf', 'sf', 'f'):
		for match_num in range(1, 100):
			entries = list(db.scouting.find({'match_num': match_num, 'match_type': match_type}))
			total_entries = len(entries)
			if not total_entries == 0:
				if match_type == 'p':
					continue  # practice matches don't matter :(
				teams = []
				for entry in entries:
					if entry['team'] in teams:
						print 'caught a wild dupe in {"team":%s, "match_type":"%s", "match_num":%s}' % (entry['team'], match_type, match_num)
					else:
						teams += [entry['team']]
				if not total_entries == 6:
					if total_entries == 1:
						suffix = 'y'
					else:
						suffix = 'ies'
					print '%s entr%s in {"match_type":"%s", "match_num":%s}' % (total_entries, suffix, match_type, match_num)
					print '\tteams: ' + str(teams)

	for entry in db.scouting.find():
		if entry['match_num'] > 100:
			print 'match ', entry['match_num'], 'contains an error'


def validate():
	"""run various validation methods (all at once, in the most efficient order possible)"""
	fix_entries()
	remove_duplicates()
	fix_team_num()
	check_matches()


def opr():
	raise Exception("Needs to be updated for new db")
	entries = []
	for match in db.sourceMatch.find({'year': 2013}):
		for color in ('red', 'blue'):
			entries.append((
				match['alliance'][color]['score'],
				match['alliance'][color]['teams'][0],
				match['alliance'][color]['teams'][1],
				match['alliance'][color]['teams'][2],
			))
	print opr(entries)
	analysis.opr()

commands = {
	'list_users': list_users,
	'add_user': add_user,
	'defaults': defaults,
	'scrape_events': scrape_events,
	'scrape_teams': scrape_teams,
	'scrape_current': scrape_current,
	'clear_db': model.db.clear,
	'backup': model.db.backup,
	'validate': validate,
	'opr': opr,
}

parser = argparse.ArgumentParser(description="A backend admin CLI to the CORE Scouting Database")
parser.add_argument('command',help=', '.join(commands.keys()))
args = parser.parse_args()

commands[args.command]()
