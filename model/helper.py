def error_dump(exception):
	"""returns an exception formatted in json so it can be returned to the client"""
	return {'error': exception.args[0]}


def check_args(supplied_data, *required_args):
	"""
		checks that the required arguments (specified in a tuple or list) exist in the supplied data
		if they don't exist, then an exception is returned
	"""
	for arg in required_args:
		if arg not in supplied_data:
			raise Exception('the argument "' + arg + '" was not supplied in your request')


def remove_defaults(data, defaults):
	"""removes default values from data and returns compressed result"""
	if type(data) is dict and type(defaults) is dict:
		compressed = {}
		for k in data:
			if k in defaults:
				if type(defaults[k]) is dict:
					compressed[k] = remove_defaults(data[k], defaults[k])
					if compressed[k] == {}:  # already know that key exists, if exactly the same then delete
						del compressed[k]
				elif not data[k] == defaults[k]:  # ensure that they are the same
					compressed[k] = data[k]
			else:
				compressed[k] = data[k]
	return compressed
