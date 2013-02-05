import importlib

def mix(app, mixins):
	for i in mixins:
		try:
			mod = importlib.import_module("api."+i)
			mod.mix(app)
		except ImportError:
			import model.log
			model.log.error("Can't import mixin " +str(i))
		except AttributeError:
			import model.log
			model.log.error("Can't import mixin " +str(i))