import web
import simplejson as json


def json_dump(variable):
	"""returns the representation of "variable" in json"""
	if web.ctx.dev:  # pretty print json in dev mode, else dump compressed json
		return json.dumps(variable, sort_keys=True, indent=4)
	else:
		return json.dumps(variable, separators=(',', ':'))


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
				elif type(data[k]) is type(structure[k]):
					structure[k] = data[k]
	return structure
