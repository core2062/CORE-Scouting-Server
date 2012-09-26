from config import DB_NAME, BACKUP_DIR
import pymongo
from time import time
import os
from simplejson import dumps, loads
import tarfile
import cStringIO as StringIO

"""
this module establishes the connection to mongo and deals with all db interaction
it is in the top level directory to make it easy to write backups to the backups folder
TODO: move into model after CWD of main.py is made into global config value
"""

c = pymongo.Connection()
database = c[DB_NAME]  # variable used in the rest of the code to access the db

#this might hold some invisible db decorators later


def check():
	"""checks that the db is setup, if not runs setup"""
	if database.user.find_one({'_id': 'admin'}) == None:  # checks if there is an admin user
		print 'setting up db in mongoDB'
		reset()


def reset():
	"""
		This script sets up or resets the entire CSD database
		It will remove all data on the site and restore the default user
		a backup will be made of the current database
	"""

	backup(DB_NAME, BACKUP_DIR + str(time()))  # backup db

	#clear out db
	c.drop_database(DB_NAME)

	#make collections
	database.create_collection('user')  # holds all the users
	database.create_collection('log')  # logging info
	database.create_collection('error')  # holds error logs for database collections, such as data that is incorrect (not programming errors)
	database.create_collection('config')  # holds configuration variables for the site

#	globalVar('analysisScoutingErrors', [])  # error log for analysisScouting
#	globalVar('analysisQueryLimits', [])  #limit what is carried into analysisScouting

	#compiled collections (holds fully compiled data and is rebuilt because data relies on multiple sources)
	database.create_collection('compiledEvent')
	database.create_collection('compiledTeam')

	#analysis collections (holds semi-compiled data and is updated rather than rebuilt, to improve performance)
	database.create_collection('semi-compiledScouting')

	#source collections (holds nearly raw data)
	database.create_collection('sourceScouting')  # data from the scouting part of the db
	database.create_collection('sourceTeam')  # scraped data on teams from the FIRST FMS
	database.create_collection('sourceEvent')  # scraped data on events
	database.create_collection('sourceMatch')  # scraped data on matches

	database.user.insert(
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


def backup(db_name, filename):
	"""
	the filename arg is the full file path that the backup should be saved to, the extension ".tar.bz2" will be automatically added
	the specified file should be not exist, if it does, the function will overwrite it

	the output is a bzipped tar archive which contains files representing the database
	each collection has its own file and in these files each document is represented as 1 line of json
	this doesn't backup indexes, gridFS files, and standard ObjectIds (the ones automatically made by mongo)
	this can also change the type of items stored in mongo due to json sterilization not storing this data
	this is used instead of the command mongodump to improve flexibility, and make it easier to call from within a python script

	consider storing each document's binary representation in files if the above issues become a problem
	"""
	filename = filename + '.tar.bz2'
	db = c[db_name]  # shortcut to db
	backup_file = tarfile.open(filename, mode='w:bz2')

	for collection in db.collection_names():
		if collection != 'system.indexes':  # auto-generated stuff... don't backup
			collection_file = StringIO.StringIO()  # make a file in the archive to hold the collection

			for document in db[collection].find({}):
				if document["_id"].__class__.__name__ == 'ObjectId': del document["_id"]  # ObjectIds aren't able to be stored in json... remove them before saving
				#return
				#if type(document["_id"])
				collection_file.write(dumps(document, separators=(',', ':')) + '\n')

			info = tarfile.TarInfo(name=collection)
			info.mtime = time()  # set time stamp
			collection_file.seek(0, os.SEEK_END)  # go to end of file
			info.size = collection_file.tell()  # get size of file based on where end is
			collection_file.seek(0)  # tar needs file to be back at beginning
			backup_file.addfile(tarinfo=info, fileobj=collection_file)  # add file to tar

	backup_file.close()


def restore(db_name, backup_file):
	"""
		this function takes a file (the type of file created by the backup() function) and restores the backed up data to the db
		db_name is the db that the contents of the backup are restored to, this db should be empty and will be dropped & overwritten if it already exists
		backup_file must be the path to the tarred backup file
	"""

	if db_name in c.database_names():  # drop existing db with same name (if there is one)
		c.drop_database(db_name)

	db = c[db_name]  # shortcut to db

	backup_tar_file = tarfile.open(backup_file)
	collection_files = backup_tar_file.getmembers()

	for collection_file in collection_files:  # each file in tar ball is a collection
		db.create_collection(collection_file.name)
		fileobj = backup_tar_file.extractfile(collection_file)

		for line in fileobj:
			db[collection_file.name].insert(loads(line))  # load a line of json and insert into db

	backup_tar_file.close()
