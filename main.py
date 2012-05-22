import web
import os
import pymongo
import simplejson as json
import model.user
#import model.errorHandler
from threading import Timer

urls = (
	'/', 'index',
	'/favicon.ico', 'favicon',
	'/user(?:/(.*))?', 'userRequest',
)
app = web.application(urls, globals())

#connect to mongo
c = pymongo.Connection()
db = c.csd


def cron():
	"""handles simple cron-like jobs such as rescraping"""
	print "cron jobs can be put here"
	t = Timer(10000, cron)
	t.start()

cron()


def loadhook():
	"""load hook for setting contextual vars"""
	web.ctx.user = model.user.user()
	web.ctx.dev = (web.input(dev='False').dev == 'True')  # if ?dev=True then dev will be set to True, otherwise it defaults to False

	inputs = web.input(username='', token='')
	#only run user.check if username and token are defined... still allow use of default guest account
	if inputs.username != '' and inputs.token != '':
		#try:
		web.ctx.user.check(username=inputs.username, token=inputs.token)  # validate user token if username and token are supplied
		#except:
		#	errorHandler()

app.add_processor(web.loadhook(loadhook))


def unloadhook():
	web.ctx.user.save()  # save incase any changes have been made to user

app.add_processor(web.unloadhook(unloadhook))


class index:
	def GET(self):
		return "<html><head><title>CSD</title></head><body>Hello, world!</body></html>"


class userRequest:
	def GET(self, name=''):
		"""handles requests for user data, logins, and signups"""
		if name == None or name == '':
			return json.dumps(web.ctx.user.safeData(), sort_keys=True, indent=4) if web.ctx.dev else json.dumps(web.ctx.user.safeData())
		elif name == 'login':
			#CONSIDER: add a delay to prevent multiple attempts

			inputs = web.input(username='', email='', password='')
			print inputs.username
			print self
			web.ctx.user.login(username=inputs.username, email=inputs.email, password=inputs.password)
		else:
			return web.application.notfound(app)  # this means it is not one of the defined meathods for interacting w/ the server


class favicon:
	def GET(self):
		"""returns the favicon, which is actually in /static"""
		return open(os.path.dirname(__file__) + '/static/favicon.ico', 'r').read()

if __name__ == "__main__":
	app.run()
