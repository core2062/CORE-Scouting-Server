import pymongo

""" this module establishes the connection to mongo and deals with all db interaction """

c = pymongo.Connection()
csd = c.csd  # variable used in the rest of the code to access the db (for now)

#this might hold some invisible db decorators
