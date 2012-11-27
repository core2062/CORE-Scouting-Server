from functools import wraps
from werkzeug import exceptions as ex
from flask import request, g

import model.user as user


def check_args(supplied_data, *required_args):
	"""
		checks that the required arguments (specified in a tuple or list)
		exist in the supplied data if they don't exist, then an exception is
		returned
	"""
	for arg in required_args:
		if arg not in supplied_data:
			raise ex.BadRequest('the argument "' + arg + '" was not supplied in your request')


def remove_defaults(data, defaults):
	"""removes default values from data and returns compressed result"""
	if type(data) is dict and type(defaults) is dict:
		compressed = {}
		for k in data:
			if k in defaults:
				if type(defaults[k]) is dict:
					compressed[k] = remove_defaults(data[k], defaults[k])

					# already know that key exists, if exactly the same then delete
					if compressed[k] == {}:
						del compressed[k]
				elif not data[k] == defaults[k]:  # ensure that they are the same
					compressed[k] = data[k]
			else:
				compressed[k] = data[k]
	return compressed


def permission_required(*permissions):
	"""
		defines a decorator for checking a user's token permissions may also
		be checked by passing all required permissions as args the user object
		handles a lot of its own authentication, but this decorator makes it
		easier to check permissions on other things like admin tasks or
		submitting data
	"""
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			# print request.json
			if 'token' in request.args.keys():
				token = request.args['token']
			elif request.json and 'token' in request.json.keys():
				token = request.json['token']
			else:
				raise ex.BadRequest('The argument token is needed for authentication')

			# store user object in g (thread safe context)
			# users may only authenticate with a token,
			# this is to prevent users from transmitting
			# their username & password with every request

			#the token gets escaped when sent, so decode it first
			g.user = user.token_auth(
				token,
				ip=request.remote_addr,
			)

			if not g.user:
				raise ex.Unauthorized('Bad token.')
			for permission in permissions:
				if not g.user.has_perm(permission):
					raise ex.Forbidden()
			return f(*args, **kwargs)
		return decorated_function
	return decorator
