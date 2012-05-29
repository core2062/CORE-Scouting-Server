import web
import mongs
import pymongo
import os

urls = (
	'(?:/)?', 'Server',
	'/([^/]*)(?:/)?', 'Database',
	# '/([^/]*)/([^/]*)', 'Collection',
	# '/([^/]*)/([^/]*)/([^/]*)/', 'Filter',
	# '/([^/]*)/([^/]*)/([^/]*)/([^/]*)/', 'Page',
	# '/([^/]*)/([^/]*)/([^/]*)/([^/]*)/([^/]*)/', 'Value',
)
app = web.application(urls, globals())


def loadhook():
	"""set up template rendering before request because web.ctx.home is not defined when the server starts up"""
	global render
	render = web.template.render(
		os.path.dirname(__file__) + '/view/',
		base='base',
		globals={'homeUrl': web.ctx.home},
	)

app.add_processor(web.loadhook(loadhook))


class Server:
	def GET(self):
		return render.server(['localhost'])


class Database:
	def GET(self, server):
		conn = pymongo.Connection(server, slave_okay=True)
		databases = sorted(conn.database_names(), key=lambda a: a.lower())
		return render.database(server, databases)

if __name__ == "__main__":
	app.run()
