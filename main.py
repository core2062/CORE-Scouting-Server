import web, os, pymongo, model.user

urls = (
	'/', 'index',
	'/favicon.ico', 'favicon',
	'/user(?:/(.*))?', 'userRequest'
)
app = web.application(urls, globals())

#connect to mongo
c = pymongo.Connection()
db = c.csd

#add in cron tasks with threading.Timer?


class index:
	def GET(self):
		return "<html><head><title>CSD</title></head><body>Hello, world!</body></html>"


class userRequest:
	user = model.user.user()  # move this into pre-hook

	def GET(self, name=''):
		"""handles requests for user data, logins, and signups"""
		if name == '':
			return name
		elif name == 'login':
			#CONSIDER: add a delay to prevent multiple attempts
			
			inputs = web.input(username='', password='')
			print inputs.username
			print self
			self.user.login(username='admin1', password='superpass')
		else:
			return web.application.notfound(app)  # this means it is not one of the defined meathods for interacting w/ the server


class favicon:
	def GET(self):
		"""returns the favicon, which is actually in /static"""
		return open(os.path.dirname(__file__) + '/static/favicon.ico', 'r').read()

if __name__ == "__main__":
	app.run()
