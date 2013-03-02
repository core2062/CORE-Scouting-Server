import argparse
import sys

import model.user


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
	model.user.new_user(name,password, email=email)

parser = argparse.ArgumentParse(description="A backend admin CLI to the CORE Scouting Database")
parser.add('command')

args = parser.parse_args

commands = {
	'list_users': model.user.list_users
	'add_user': add_user
}

commands[args.command]()