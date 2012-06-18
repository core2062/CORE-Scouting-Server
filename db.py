import pymongo
import subprocess
from time import time
import os

"""
	this module establishes the connection to mongo and deals with all db interaction
	it is in the top level directory to make it easy to write backups to the backups folder
"""

cwd = os.path.dirname(__file__) + '/'  # get current working directory

c = pymongo.Connection()
csd = c.csd  # variable used in the rest of the code to access the db (for now)

#this might hold some invisible db decorators later


def check():
	"""checks that the db is setup, if not runs setup"""
	if csd.user.find_one({'_id': 'admin'}) == None:  # checks if there is an admin user
		print 'setting up mongoDB'
		reset()


def reset():
	"""
		This script sets up or resets the entire CSD database
		It will remove all data on the site and restore the default user
		a backup will be made of the current database
	"""

	# backup db
	subprocess.call([
		"mongodump",
		"out " + cwd + 'backup/' + str(time()),
		'db csd'
	])

	#clear out db
	c.drop_database('csd')

	#make collections
	csd.create_collection('user')
	csd.create_collection('log')
	csd.create_collection('error')  # holds error logs for database collections, such as data that is incorrect (not programming errors)
	csd.create_collection('config')  # holds configuration variables for the site

#	globalVar('analysisScoutingErrors', [])  # error log for analysisScouting
#	globalVar('analysisQueryLimits', [])  #limit what is carried into analysisScouting

	#compiled collections (holds fully compiled data and is rebuilt because data relies on multiple sources)
	csd.create_collection('compiledEvent')
	csd.create_collection('compiledTeam')

	#analysis collections (holds semi-compiled data and is updated rather than rebuilt, to improve performance)
	csd.create_collection('semi-compiledScouting')

	#source collections (holds nearly raw data)
	csd.create_collection('sourceScouting')
	csd.create_collection('sourceFMS')
	csd.create_collection('sourceTeamInfo')
	csd.create_collection('sourceEventInfo')

	csd.user.insert(
		{  # initialized with defaults (for guest user)
			'_id': 'admin',
			'account': {
				'password': 'superpass',
			},
			'permission': [  # this user has permissions to do everything
				'input',
				'run_admin_task',
			],
		}
	)
