import os

"""
	this file holds configuration variables for the csd. these variables are used throughout the code, but are stored here to make changing configuration easier. there are also a few variables which are dynamically set and store info about the enviroment that the CSD is running in
"""

#filesystem
CWD = os.path.dirname(__file__) + '/'  # get current working directory (top level of the csd server folder)
BACKUP_DIR = CWD + 'backup/'  # where db backups are put

#MongoDB
DB_NAME = 'csd'


# check that mongo is setup during startup... this can be dangerous if you remove the admin user; not having "admin" will trigger a db reset if this check runs so you may want to disable this in production. it is enabled by default because the db will need to be setup during the first run.
ENABLE_DB_SETUP_CHECK = True
