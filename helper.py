from config import app
from functools import wraps
from werkzeug import exceptions as ex
from flask import request, g, make_response

import model.user as user


def check_args(*required_args):
	"""
	checks that the required arguments (specified in a tuple or list) exist in
	the supplied data if they don't exist, then an exception is raised
	"""
	for arg in required_args:
		if arg not in g.args:
			raise ex.BadRequest('the argument "%s" was not supplied in your request' % arg)


def args_required(*args):
	def decorator(f):
		@wraps(f)
		def decor(*arg, **kwargs):
			check_args(*args)
			return f(*args, **kwargs)
		return decor
	return decorator


def allow_origins(func=None, origins=app.config["ALLOWED_ORIGINS"]):
	def wrapped(func):
		@wraps(func)
		def decorated(*args, **kwargs):
			origin = request.headers.get('Origin')
			g.cors = True  # origin in origins
			if request.method == 'OPTIONS':
				response = make_response('ok')
				response.headers['Access-Control-Allow-Origin'] = origin
				response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
				return response
			return func(*args, **kwargs)
		return decorated
	if func:
		return wrapped(func)
	else:
		return wrapped


@app.after_request
def after_request(response):
	if getattr(g, 'cors', False):
		response.headers['Access-Control-Allow-Origin'] = (
			request.headers['Origin']
		)
		response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
	return response
