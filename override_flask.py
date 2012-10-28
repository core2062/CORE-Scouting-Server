from flask import Flask, Response, request, jsonify
import simplejson
from simplejson import dumps
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

"""this holds overrides to modify flask"""


class Flask(Flask):
	"""
		override the make_response method to:
			allow json to be returned by view functions
			run functions directly after the view functions
	"""

	# A list of functions that should be called directly after the view functions are finished
	# these can be used to post-process the returned value of the view functions
	# To register a function here, use the :meth:`after_view` decorator
	# this should be in init with the rest of the function lists, but this way it won't override the regular init
	after_view_funcs = []

	def after_view(self, f):
		"""Registers a function to run directly after the view functions"""
		self.after_view_funcs.append(f)
		return f

	def make_response(self, rv):
		"""Converts the return value from a view function to a real
		response object that is an instance of :attr:`response_class`.

		The following types are allowed for `rv`:

		======================= ===========================================
		:attr:`response_class`  the object is returned unchanged
		:class:`str`			a response object is created with the
								string as body
		:class:`unicode`		a response object is created with the
								string encoded to utf-8 as body
		:class:`tuple`  		the response object is created with the
								contents of the tuple as arguments
		a WSGI function 		the function is called as WSGI application
								and buffered as response object
		a dict or list			causes rv to be formatted into json and
								returned
		======================= ===========================================

		:param rv: the return value from the view function
		"""

		for func in self.after_view_funcs:
			func_rv = func(rv)  # call each function with the return value as the only parameter
			if func_rv is not None:
				rv = func_rv  # like all the other types of functions, if it returns something, that gets sent instead
				break

		if type(rv) in (dict, list):  # format the response in json if it is a variable (not html being returned)
			if self.debug:  # pretty print json in dev mode, else dump compressed json
				json = dumps(rv, sort_keys=True, indent=4)
			else:
				json = dumps(rv, separators=(',', ':'))
			rv = Response(json, mimetype='application/json')

		if rv is None:
			raise ValueError('View function did not return a response')
		if isinstance(rv, self.response_class):
			return rv
		if isinstance(rv, basestring):
			return self.response_class(rv)
		if isinstance(rv, tuple):
			return self.response_class(*rv)
		return self.response_class.force_type(rv, request.environ)

def make_json_app(import_name, **kwargs):
    """
    Creates a JSON-oriented Flask app.

    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):

    { "message": "405: Method Not Allowed" }
    """
    def make_json_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
        return response

    app = Flask(import_name, **kwargs)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    return app

class MagicJSONEncoder(simplejson.JSONEncoder):
    def default(s, o):
        if getattr(o,'__json__',None):
            return o.__json__()
        else:
            raise TypeError(repr(o) + " is not JSON serializable")

simplejson.JSONEncoder = MagicJSONEncoder

