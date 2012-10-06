#CORE Scouting Database Server

The CSD itself acts as a web service and is separated from the client. It only returns machine readable data (in json) and other resources like csv exports from the database. The client acts as a viewer for this data and presents it in a human readable form. By keeping this separation, the CSD maintains an API that can be easily used by other programs while still being human readable (unlike the FIRST FMS which is neither human-readable nor machine-readable).

###Installation
 - install Python 2.7
 - [install MongoDB](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-debian-or-ubuntu-linux/)
 - `sudo pip install Flask simplejson pymongo`
 - clone this repo
 - run the server with `python path-to-repo/CORE-Scouting-Server/main.py`

*in production, you should run the server with gunicorn behind a nginx reverse-proxy

###Notes
many teams change names, merge, split... etc. the db has no way of tracking this or representing this

data on events before 2003 is not available on the FIRST FMS DB... team history can go back this far

2000 and prior award listings may be incomplete on the FIRST FMS DB

teams which have not been active during the past 3 years are purged from the frc database ... see: http://www.team358org/files/team_lookup/

contact FIRST and see if they still have any of this data?