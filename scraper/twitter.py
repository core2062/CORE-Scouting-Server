
from os import path
from twython import Twython

keys = map(str.strip, list(open(path.join(path.dirname(__file__),"TWITTER_CONFIG"))))
# Where TWITTER_CONFIG is a file containing API_KEY, API_SECRET, and ACCESS_TOKEN on each line

twitter = Twython(keys[0], access_token=keys[2])

def get_matches(year = 2014):
	twitter.show_user("")

def get_tweets():
	tweets = []
	user_timeline = twitter.get_user_timeline(screen_name='frcfms',count=200)
	print len(user_timeline)
	for tweet in user_timeline:
	    tweets.append(tweet['text'])
	# Count could be less than 200, see:
	# https://dev.twitter.com/discussions/7513
	while len(user_timeline) != 0: 
	    user_timeline = twitter.get_user_timeline(screen_name='frcfms',count=200,
	    	max_id=user_timeline[len(user_timeline)-1]['id']-1)
	    print len(user_timeline)
	    for tweet in user_timeline:
	        tweets.append(tweet['text'])
	        if '2013' in tweet['created_at']:
	        	break
	        else:
	        	print tweet['created_at']
	print len(tweets)
	return tweets