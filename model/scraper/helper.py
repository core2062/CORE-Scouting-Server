import re
import urllib2

# a URL that gives us a result with urls that have session keys in them (response only shows 25 results from FMS DB... pretty small request)
SESSION_KEY_GENERATING_PATTERN = "https://my.usfirst.org/myarea/index.lasso?page=searchresults&programs=FRC&reports=teams&omit_searchform=1&season_FRC=%s"
SESSION_RE = re.compile(r'myarea:([A-Za-z0-9]*)')


def url_fetch(url):
	"""
	gets the url specified and returns the content
	caching of pages from previous years (non-changing pages) could be implemented in this function to speed up testing of new scrapers
	"""

	try:
		return urllib2.urlopen(url, timeout=60).read()
	except urllib2.URLError, e:  # raise a better error
		raise Exception('unable to retrieve url: ' + url + ' reason:' + str(e.reason))


def get_session_key(year):
	"""
	Grab a page from FIRST so we can get a session key out of URLs on it.
	This session key is needed to construct working event detail information URLs.

	FIRST session keys are season-dependent. A session key retrieved from a 2011 page does not work to get information about 2012 events.
	Every request must also know what year it is for.
	"""

	regex_results = re.search(SESSION_RE, url_fetch(SESSION_KEY_GENERATING_PATTERN % year))

	if regex_results is not None:
		session_key = regex_results.group(1)  # first parenthetical group
		if session_key is not None:
			return session_key

	#else: (if above didn't return)
	raise Exception('unable to extract session key from result')
