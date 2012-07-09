import pymongo
import subprocess
from time import time
import os
from simplejson import dumps
import tarfile
import cStringIO as StringIO

"""
	this module establishes the connection to mongo and deals with all db interaction
	it is in the top level directory to make it easy to write backups to the backups folder
	TODO: move into model after CWD of main.py is made into global config value
"""

cwd = os.path.dirname(__file__) + '/'  # get current working directory

c = pymongo.Connection()
csd = c.csd  # variable used in the rest of the code to access the db (for now)

#this might hold some invisible db decorators later


# def check():
# 	"""checks that the db is setup, if not runs setup"""
# 	if csd.user.find_one({'_id': 'admin'}) == None:  # checks if there is an admin user
# 		print 'setting up mongoDB'
# 		reset()


def reset():
	"""
		This script sets up or resets the entire CSD database
		It will remove all data on the site and restore the default user
		a backup will be made of the current database
	"""

	backup(cwd + 'backup')  # backup db

	#clear out db
	c.drop_database('csd')

	#make collections
	csd.create_collection('user')  # holds all the users
	csd.create_collection('log')  # logging info
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
	csd.create_collection('sourceScouting')  # data from the scouting part of the db
	csd.create_collection('sourceTeam')  # scraped data on teams from the FIRST FMS
	csd.create_collection('sourceEvent')  # scraped data on events
	csd.create_collection('sourceMatch')  # scraped data on matches

	csd.user.insert(
		{
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


def backup(filename):
	"""
	the filename arg is the full file path that the backup should be saved to, the extension ".tar.bz2" will be automatically added
	the specified file should be not exist, if it does, the function will overwrite it

	the output is a bzipped tar archive which contains files representing the database
	each collection has its own file and in these files each document is represented as 1 line of json
	this doesn't backup gridFS files
	this is used instead of the command mongodump to improve flexibility, and make it easier to call from within a python script
	"""
	filename = filename + '.tar.bz2'

	backup_file = tarfile.open(filename, mode='w:bz2')

	for collection in csd.collection_names():
		if collection != 'system.indexes':  # auto-generated stuff... don't backup
			collection_file = StringIO.StringIO()  # make a file in the archive to hold the collection

			for document in csd[collection].find({}):
				document["_id"] = str(document['_id'])  # regular document _ids aren't able to be converted to json, so make it a string
				collection_file.write(dumps(document, separators=(',', ':')) + '\n')

			info = tarfile.TarInfo(name=collection)
			info.mtime = time()  # set time stamp
			collection_file.seek(0, os.SEEK_END)  # go to end of file
			info.size = collection_file.tell()  # get size of file based on where end is
			collection_file.seek(0)  # tar needs file to be back at beginning
			backup_file.addfile(tarinfo=info, fileobj=collection_file)  # add file to tar

	backup_file.close()
