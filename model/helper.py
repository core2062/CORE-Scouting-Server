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
	return json_dump({'error': exception.args[0]})


def subtract_dict(a, b):
	"""Remove the keys in b from a"""
	for k in b:
		if k in a:
			if isinstance(b[k], dict):
				subtract_dict(a[k], b[k])
			else:
				del a[k]

data = {
	'_id': 'guest',
	'account': {
		'password': '',
		'email': '',
	},
	'prefs': {
		'fade': True,
		'verbose': True,
	},
}

data2 = {
	'_id': 'tomato',
	'account': {
		'password': '',
		'email': '',
	},
	'permission': [
		'input',
	],
	'info': {
		'fName': '',
		'lName': '',
		'team': 0,
	},
	'prefs': {
		'fade': False,
		'verbose': True,
	},
	'opt': {
		'zip': '',
		'browser': '',
		'gender': '',
	},
	'session': {
		'ip': '',
		'startTime': '',
		'token': '',
	},
	'log': {},
}

subtract_dict(data, data2)

print data2
print data