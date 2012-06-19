directory structure:

	model - holds all logic for CSD
		scraper
		analysis
			opr
		input
		user - model for user. includes methods for logout, signup, updating mongo, and permissions
	view - holds code for building response to client request. mostly for getting data in json to present because templating is done client-side, and also generates csv exports
	controller - interacts with client, determines what code to do with request or runs client builder
		cron - handles rescraping / updating at particular times
		request - one big object for dealing with requests and some code for permissions
	client - this is separate from the server. the client is neither a view nor a controller, but contains separate logic for interacting with the server. 
		builder - this contains scripts for building the client which, when built, will be separate from the server, and will interact via ajax with the server's controller
		extender - used to deliver pages to the client, on demand, so not everything needs to be embedded by the builder. functions similar to the builder
		temp - holds cache for files used by builder
			cache - holds pre-built clients (copy of the html/css/js that is sent to user) with different embedded pages
			css
			js
		resources
			less - holds source files in less which later get compiled into css
			path - holds html representation in PATH code... or I might switch to a templating language python
			coffee - holds source files in coffee script which later get compiled into js
			font
			img
			favicon.ico

The CSD itself acts as a web service and is separated from the client. It only returns machine readable data (in json) and other resources like csv exports from the database. The client acts as a viewer for this data and presents it in a human readable form. By keeping this separation, the CSD maintains an API that can be easily used by other programs while still being human readable (unlike the FIRST FMS which is neither human-readable nor machine-readable).

NOTES
 - use random _id for normal usernames (login with only email) and special username for admin / guest



 many teams change names, merge, split... etc. the db has no way of tracking this or representing this

 data on events before 2003 is not available on the FIRST FMS DB... team history can go back this far
 2000 and prior award listings may be incomplete on the FIRST FMS DB

 teams which have not been active during the past 3 years are purged from the frc database ... see: http://www.team358.org/files/team_lookup/

 contact FIRST and see if they still have any of this data?