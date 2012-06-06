import web
import mongs
import os
import re
import datetime
import pprint  # check this
import urllib  # check this
import simplejson as json
import pymongo
from bson.objectid import ObjectId, InvalidId

cwd = os.path.dirname(__file__) + '/'  # get current working directory

# urls are formatted as /server/database/collection/{}{}/page.contenttype
# the first {} is where a filter can be used
# the second {} is where a sort can be optionally added
# the page & file extension are not required (they have defaults)

# (/|.html|.json)? provides a (usually) optional slash or file extension at the end
# for a url like http://lh/serv/db/coll.word a slash must be added to the end to show that "word" is not a file extension
# the slash does nothing but the file extensions modify the return type

urls = (
	'', 'Server',
	r'/([^/]*)', 'Database',
	r'/([^/]*)/([^/]*)', 'Collection',
	r'/([^/]*)/([^/]*)/([^/]*)', 'Filter',
	r'/([^/]*)/([^/]*)/([^/]*)/{([^(}/)]*)}(?:/([^/]*))?', 'Page',
	# r'/([^/]*)/([^/]*)/([^/]*)/([^/]*)/([^/]*)', 'Value',
)
app = web.application(urls, globals())

render = ''  # just to show that it is declared globally

# pre-compile regex for normalization to improve performance
# this assumes that a file extension will have between 1 and 4 letters after the dot (not always true... just a lazy match)
normalizeRegex = re.compile(r'(/|\.[a-z]{1,4})?$')


def loadhook():
	"""
		set up template rendering before request because sadly web.ctx.home is not defined when the server starts up
		normalize url (remove optional "/" and get return type)
	"""
	global render
	render = web.template.render(
		cwd + 'view/',
		base='base',
		globals={'homeUrl': web.ctx.home},
	)

	extension = normalizeRegex.search(web.ctx.path).group(0)  # get file extension (sorta) if there is one
	web.ctx.path = re.sub(extension + '$', '', web.ctx.path)  # remove the extension from the end ($) of the url

	if extension in ('/', '.html', ''):  # list of extra extensions which mean same thing & are tolerated
		web.ctx.contentType = 'html'  # set default content type
	elif extension in ('.json'):  # list of supported extensions (.html is not listed here because it is default)
		web.ctx.contentType = extension[1:]  # set content type (with "." removed)
	else:
		raise Exception('unsupported content type requested (garbage at end of url)')

	print web.ctx.path
	print web.ctx.contentType

app.add_processor(web.loadhook(loadhook))


class Server:
	"""provides a listing of servers"""
	def GET(self):
		return render.server(['localhost'])  # TODO: move this var into a config file


class Database:
	"""lists databases avaliable on a given server"""
	def GET(self, server):
		conn = pymongo.Connection(server, slave_okay=True)
		databases = sorted(conn.database_names(), key=lambda a: a.lower())
		return render.database(server, databases)


class Collection:
	"""lists collections avaliable in a given database"""
	def GET(self, server, database):
		MB = 1024 ** 2.0

		def f2s(n, scale=1.0):
			"""Given float, return str"""
			if n == 0.0:
				out = "0&nbsp;&nbsp;"
			else:
				out = web.commify(round(n / scale, 1))
			return out

		class Mongo_Collection(object):
			"""Model a MongoDB collection"""

			is_index = False

			def __init__(self, db, collname):
				self.name = collname
				self.stats = stats = db.command({'collStats': collname})
				self.storage_size = float(stats['storageSize'])
				self.data_size = float(stats['size'])

				# I adapted this from the definition of db.foo.totalSize per the mongo
				# js shell. I gather from there that indexes are just specially-named
				# collections, and the same storageSize/dataSize semantics apply. I
				# believe that the indexSizes attribute of collStats gives us dataSize.
				index_names = stats['indexSizes'].keys()
				self.indices = ["%s.$%s" % (collname, name) for name in index_names]

			def format_storage_size(self, dbsize):
				total = f2s(dbsize, MB).replace("&nbsp;", "N")

				absolute = f2s(self.storage_size, MB)
				absolute = absolute.replace("&nbsp;", "N")
				absolute = ("&nbsp;" * (len(total) - len(absolute))) + absolute
				absolute = absolute.replace("N", "&nbsp;")
				absolute = "%s&nbsp;&nbsp;" % absolute

				percent = f2s(self.storage_size / dbsize * 100)
				percent = ((6 - len(percent)) * "&nbsp;") + percent

				return absolute + percent

			def format_data_size(self, dbsize):
				"""Return a string indicating dataSize.
				"""
				out = f2s(self.data_size / dbsize * 100)
				out = out.replace("&nbsp;", "N")
				out = ("&nbsp;" * (4 - len(out))) + out
				out = out.replace("N", "&nbsp;")
				return out

		class Index(Mongo_Collection):
			"""
			MongoDB indices are special collections.

			The storageSize and dataSize semantics appear to be the same, so all of the
			logic of the base class applies. We just want to format them differently in
			the UI.

			"""
			is_index = True

		conn = pymongo.Connection(server, slave_okay=True)
		db = conn[database]

		# optimize
		# The collection_names API call is unsuitable for databases with many
		# collections. In such cases we require the user to browse the collections via
		# the system.namespaces meta-collection.

		if db['system.namespaces'].count() > 256:
			return web.Found('./system.namespaces/')

		# We need the disk size of the database as a whole in order to calculate
		# percentages. However, the dbstats call blocks the whole db server while it
		# runs, and it takes a long time (we killed it after 15 minutes in the case
		# where this problem came to light. Oops!). See:
		#
		#   http://www.mongodb.org/display/DOCS/Monitoring+and+Diagnostics#MonitoringandDiagnostics-mongoShellDiagnosticCommands
		#
		# Now instead we sum storageSize from collstats, which is a safe call (per
		# jaraco). Apparently there are three size metrics, however, and I'm not sure
		# that summing collstats.storageSize is guaranteed to equal dbstats.fileSize
		# (which is what I want). Here's me trying to figure out what to do:
		#
		#   http://stackoverflow.com/questions/10339852/
		#
		# The bottom line for now is that I'm showing storageSize and dataSize and
		# pretending not to care about fileSize (though of course that's the very thing
		# I care about!).
		#
		# Update: I've filed an issue with 10gen to see about safely exposing fileSize
		# per-db and per-collection in a future release.

		dbsize = 0.0

		# We have to build this as a list rather than using a generator because we need
		# to fully compute dbsize before formatting any given row for display. We also
		# take pains to sort by storage_size, with indices grouped by collection.

		rows = []
		collnames = db.collection_names()
		if collnames:
			collnames += ['system.namespaces']

		# first build a list of collections, sorted by storage_size ascending
		for collname in collnames:
			rows.append(Mongo_Collection(db, collname))
			dbsize += rows[-1].storage_size
		rows.sort(key=lambda row: row.storage_size)

		# now add in indices, reversing in the process (we want biggest first)
		_rows = []
		while rows:
			collection = rows.pop()  # this has the effect of reversing rows
			_rows.append(collection)
			indices = []
			for indexname in collection.indices:
				indices.append(Index(db, indexname))
				dbsize += indices[-1].storage_size
			indices.sort(key=lambda index: index.storage_size, reverse=True)
			_rows.extend(indices)
		rows = _rows

		dbsize_str = f2s(dbsize, MB)

		return render.collection(database, server, rows, dbsize, dbsize_str)


class Filter:
	"""directs user to query for docs in collection or returns no docs found"""
	def GET(self, server, database, collection):
		coll = pymongo.Connection(server, slave_okay=True)[database][collection]

		if collection == 'system.namespaces':
			# Special case. This collection holds the names of all other collections in
			# this database. Users can access it directly for any database. For
			# databases with more than a few collections we enforce that users browse
			# collections using this interface rather than calling collection_names.

			documents = coll.find()
			if documents.count() < 1024:  # assume that system.namespaces isn't indexed
				documents.sort('name', pymongo.ASCENDING)
		else:
			#query for a "normal" collection.
			documents = coll.find({'_id': {'$exists': True}}).sort('_id', pymongo.ASCENDING)

		try:
			documents.next()
		except StopIteration:
			pass
		else:
			# redirect users to the first document in this collection if too large for single return
			return web.Found('%s/%s/%s/%s/{}/1' % (web.ctx.home, server, database, collection))

		return render.filter(server, database, collection)  # no documents in collection


class Page:
	def GET(self, server, database, collection, filter, page=None):
		SIZE_THRESHOLD = 2048  # number of bytes above which we link out

		class Pair:
			"""Represent a single key/value pair from a document"""

			is_filtered = False
			is_indexed = False

			def __init__(self, base, _id, k, v):
				escape = True
				if isinstance(v, unicode):
					# lists and dictionaries work for some reason
					v = v.encode('ASCII', 'replace')
				if isinstance(v, ObjectId):
					v = '%s (%s)' % (v, v.generation_time)
				if isinstance(v, datetime.datetime):
					v = "%s (%s)" % (v.isoformat(), mongs.dt2age(v))
				if isinstance(v, (int, float)):
					v = "<code>%s</code>" % v
					escape = False
				nv = len(str(v))
				link = ''
				if k == '_id':
					link = "%s/%s/" % (base, _id)
				elif _id and nv > SIZE_THRESHOLD:
					v = "%d bytes" % nv
					link = "%s/%s/%s.json" % (base, _id, k)
				else:
					if not isinstance(v, basestring):
						v = pprint.pformat(v, indent=1)
					if escape:
						v = v.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
					if '\n' in v:
						v = "<pre>%s</pre>" % v

				self.k = k
				self.v = v
				self.link = link

		def NamespacePair(database):
			# Have I ever done this before? I don't think I have.

			class NamespacePair(Pair):
				"""Represent the single pair of values for a system.namespaces entry.
				"""
				def __init__(self, base, _id, k, v):
					parts = v.split('.$')
					if len(parts) == 1:
						parts += ['']
					namepart, indexpart = parts
					if indexpart:
						indexpart = ".$" + indexpart
					collection = namepart[len(database) + 1:]
					value = '%s.<a href="../../../%s/">%s</a>%s'
					value %= (database, collection, collection, indexpart)

					self.k = k
					self.v = value
					self.link = False

			return NamespacePair

		single = page is None
		#filtered = single

		# Pair class
		# If we are on system.namespaces we want to link to collections.

		if collection == 'system.namespaces':
			Pair = NamespacePair(database)  # will insert hyperlinks to the collection

		# Compute base, filter, and page
		# This simplate is symlinked to be called in two contexts:
		#
		# - when a document is specified by a page number into a number of documents
		#    matched by a filter
		# - when a single document is specified by its _id
		#
		# Base is used to compute links, filter is the query spec, and page is the
		# 1-index into the query results.

		optimize_count = False  # If we can, compute the count without filtering.

		if not single:      # /server/database/collection/filter/page/
			# Parse the filter as JSON, possibly base64-encoded.
			base = '../..'
			filter = urllib.unquote_plus(filter).strip()
			if filter:
				#filtered = True
				if not filter.startswith('{'):
					filter = filter.decode('base64')
				filter = json.loads(filter)
			else:
				filter = {}
			if not filter:
				# If there is no filter, we can safely compute the count from the
				# unfiltered collection, which appears to be O(1) instead of O(N).
				optimize_count = True

		elif collection == 'system.namespaces':
							# /server/database/system.namespaces/collection/

			# Special case for system.namespaces. The _id is actually the
			# fully-qualified name of a collection or index. Send them to the
			# collection!
			collection = filter.split('$')[0][len(database) + 1:]
			return web.redirect('../../%s/' % collection)

		else:  # /server/database/collection/_id/
			# Convert a request for a specific _id into a filter with one page.
			page = 1
			base = '..'
			_id = filter
			try:
				_id = ObjectId(_id)
			except InvalidId:
				pass
			filter = {"_id": _id}

		if collection == 'system.namespaces':
			# special case for MongoDB's collection of collections; docs have no _id
			pass
		else:
			if '_id' not in filter:
				# I'm sorry, I forget why I did this. :^(
				filter.update({'_id': {'$exists': True}})

		# Sort
		# The user passes sort in as part of the {filter} hash, which otherwise is a
		# MongoDB query spec. Pull sort out after the filter has been decoded but
		# before we actually use it.

		if 'sort' in filter:
			sort = filter.pop('sort')
		elif collection == 'system.namespaces':
			# special case; this has no _id, only name
			sort = [("name", 1)]
		else:
			sort = [("_id", 1)]

		# Load documents
		# pymongo.Connection advertises that it does connection pooling.

		coll = pymongo.Connection(server, slave_okay=True)[database][collection]
		documents = coll.find(filter)
		ndocs = coll.count() if optimize_count else documents.count()
		if (page < 1) or (page > ndocs):
			return web.application.notfound(app)
		documents.rewind()

		# Sort

		if collection == 'system.namespaces' and ndocs > 1024:

			# Special case. It is possible to index system.namespaces, but no one is
			# really going to have done that. Only sort if there's a small number of
			# collections.
			#
			# The next step would be to check for the presence of an index. I think
			# MongoDB actually does this internally (refuses to sort if the result set
			# is too large and there's no index), but I think it still degrades
			# performance.

			pass

		else:
			documents.sort(sort)

		# Compute prev/next
		prev = None  # or int
		next = None  # or int
		if page > 1:
			prev = page - 1
		if page < ndocs:
			next = page + 1

		# Advance the cursor to the requested document
		# This appears to be O(N), which means it is fast for early pages and slow for
		# late pages.

		document = documents.skip(page - 1).next()

		# Compute a set of indexed keys
		indices = coll.index_information()
		indexed = set()
		for v in indices.values():
			indexed.add(v['key'][0][0])

		# Convert the document to a generator for the template
		if document is not None:  # XXX Can document ever be None?
			_id = document.get('_id', '')

			def generate_pairs(document):
				"""Yield key/value pairs for document.
				"""
				for k, v in sorted(document.iteritems()):
					pair = Pair(base, _id, k, v)
					pair.is_filtered = False
					pair.is_indexed = pair.k in indexed
					pair.sort = ''
					if pair.k != '_id':
						pair.is_filtered = pair.k in filter
						if pair.k == sort:
							pair.sort = 'ascending' if direction > 0 else 'descending'
					yield pair
			pairs = generate_pairs(document)
			if single:
				# For documents that were specified by an explicit _id, we show
				# that _id above the rest of the key/values. Advancing the pairs
				# generator here means that we don't display _id again with the
				# rest of the key/values.
				pairs.next()
		return render.server(['localhost'])


class Value:
	def GET(self, server, database, collection, filter, page):
		return render.server(['localhost'])

if __name__ == "__main__":
	app.run()
