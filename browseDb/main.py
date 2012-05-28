import web
import mongs

urls = (
	'/', 'Server',
)
app = web.application(urls, globals())

render = web.template.render('view/', base='base')


class Server:
	def GET(self):
		servers = mongs.get('servers', 'localhost')
		servers = [server.strip(',') for server in servers.split()]
		servers = [server for server in servers if server]
		servers.sort()
		render.server(servers)


if __name__ == "__main__":
	app.run()
