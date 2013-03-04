#CORE Scouting Database Server
------------------------------

The CSD itself acts as a web service and is separated from the client. It only returns machine readable data (in json) and other resources like csv exports from the database. The client acts as a viewer for this data and presents it in a human readable form. By keeping this separation, the CSD maintains an API that can be easily used by other programs while still being human readable (unlike the FIRST FMS which is neither human-readable nor machine-readable).

###Installation
 - install Python 2.7
 - [install MongoDB](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-debian-or-ubuntu-linux/)
 - `sudo pip install Flask simplejson pymongo jsonschema`
 - clone this repo
 - run the server with `python path-to-repo/CORE-Scouting-Server/main.py`

*in production, you should run the server with gunicorn behind a nginx reverse-proxy

###Notes
many teams change names, merge, split... etc. the db has no way of tracking this or representing this

----------------------
[(Ↄ)](http://www.gnu.org/licenses/gpl.html) 2011-2012 FIRST Robotics Team, CORE 2062