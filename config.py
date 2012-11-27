import os

"""
	this file holds configuration variables for the csd.
	these variables are used throughout the code, but are stored here
	to make changing configuration easier. There are also
	a few variables which are dynamically set and store info
	about the enviroment that the CSD is running in
"""

#filesystem
CWD = os.getcwd() + '/'  # get current working directory (top level of the csd server folder)
BACKUP_DIR = CWD + 'backup/'  # where db backups are put
SCHEMA_DIR = CWD + 'schema/'

#MongoDB
DB_NAME = 'csd'

# allowing tokens to be moved to a different ip address could allow an attacker to more easily hijack a session, but not allowing it could require users to login more often
ALLOW_TOKENS_TO_CHANGE_IP = True

TOKEN_LENGTH = 20
SALT_LENGTH = 20

#only used while setting up db (for guest & admin account)
#admin password should be changed directly after setting up db
DEFAULT_PASSWORD = 'guest'

CURRENT_EVENT = 'wi'
