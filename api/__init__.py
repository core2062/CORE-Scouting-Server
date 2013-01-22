import importlibs

def mix(app, mixins):
	for i in mixins:
		try:
			mod = importlibs.import_module(i)
			mod.mix(app)
		except ImportError:
			import model.log
			model.log.error("Can't import mixin " +str(i))