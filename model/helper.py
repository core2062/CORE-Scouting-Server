def error_dump(exception):
	"""returns an exception formatted in json so it can be returned to the client"""
	return {'error': exception.args[0]}


def restrictive_merge(data, structure):
	"""
		merges data into structure without adding or removing any keys in structure or changing any data types
		this can be used to provide a basic validation of the structure / type of user provided data
	"""
	if type(data) is dict and type(structure) is dict:
		for k in structure:
			if k in data:
				if type(structure[k]) is dict:
					structure[k] = restrictive_merge(data[k], structure[k])
				elif type(data[k]) is type(structure[k]):  # ensure that types match
					structure[k] = data[k]
	return structure


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


def check_args(required_args, supplied_data):
	"""
		checks that the required arguments (specified in a tuple or list) exist in the supplied data
		if they don't exist, then an exception is returned
	"""
	for arg in required_args:
		if arg not in supplied_data:
			raise Exception('the argument "' + arg + '" was not supplied in your request')
