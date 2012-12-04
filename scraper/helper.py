import re
import urllib2
import os
from BeautifulSoup import BeautifulSoup, Comment

from config import CACHE_DIR

# a URL that gives us a result with urls that have session keys in them
# (response only shows 25 results from FMS DB... pretty small request)
SESSION_KEY_GENERATING_PATTERN = "https://my.usfirst.org/myarea/index.lasso?page=searchresults&programs=FRC&reports=teams&omit_searchform=1&season_FRC=%s"
SESSION_RE = re.compile(r'myarea:([A-Za-z0-9]*)')

# stuff to be cut out of html (to reduce file size)
CRAP_ATTRIBUTES = (
	'style',
	'cellpadding',
	'cellspacing',
	'valign',
	'align',
	'height',
	'width',
	'bgcolor',
	'onmouseout',
	'onmouseover',
)
CRAP_TAGS = ('script', 'img', 'style')


def url_fetch(url, cache=True, soup=True):
	"""
	gets the url specified and returns the content cache tells if the page
	should be. cached and if a cached version should be loaded from the cache.
	if soup is true, a beautiful soup object will be returned (with some of
	the crap cut out)
	"""
	saved = False

	filename = CACHE_DIR + url[url.index(':') + 3:]
	try:
		#if there's a session key attached, remove it... it shouldn't be in
		#the file name
		filename = filename[:filename.index('&-session=myarea:')]
	except:
		pass
	if cache == True and os.path.exists(filename):
		content = open(filename, 'r').read()
		saved = True
	else:
		try:
			content = urllib2.urlopen(url, timeout=60).read()
		except urllib2.URLError, e:  # raise a better error
			raise Exception(
				'unable to retrieve url: %s reason:' % url + str(e.reason)
			)

	if soup:
		content = BeautifulSoup(content)

	if(cache and not saved):
		if soup:
			#remove crap (non-data) from html
			for tag in content.findAll(True):
				if tag.name in CRAP_TAGS:
					tag.decompose()

				for attribute in CRAP_ATTRIBUTES:
					del tag[attribute]

			comments = content.findAll(text=lambda text: isinstance(text, Comment))
			for comment in comments:
				comment.extract()

		# if content is beautiful soup, str will make it into a string
		cache_file(str(content), filename)

	return content


def cache_file(content, filename):
	try:
		os.makedirs(os.path.dirname(filename))
	except:
		pass

	open(filename, 'w').write(content)
	print 'cached ' + filename


def get_session_key(year):
	"""
	Grab a page from FIRST so we can get a session key out of URLs on it.
	This session key is needed to construct working event detail information URLs.

	FIRST session keys are season-dependent. A session key retrieved from a
	2011 page does not work to get information about 2012 events. Every
	request must also know what year it is for.
	"""

	regex_results = re.search(
		SESSION_RE,
		url_fetch(SESSION_KEY_GENERATING_PATTERN % year, False, False)
	)

	if regex_results is not None:
		session_key = regex_results.group(1)
		if session_key is not None:
			return session_key

	#else: (if above didn't return)
	raise Exception('unable to extract session key from result')
