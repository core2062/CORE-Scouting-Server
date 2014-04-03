import requests
from operator import attrgetter

from model.log import log
from model.db import database as db
from model import fms

h_id = {"X-TBA-App-Id": "core2062:scouting:dev"}
domain = "http://thebluealliance.com/api/"

def tba_call(endpoint, *args, **kwargs):
    r = requests.get(domain+(endpoint.format(*args)), headers=h_id, **kwargs)
    if not r.ok:
        log('error', "tba call error", str(r.status_code), endpoint, r.text)
        r.raise_for_status()
    return r.json()

def event(ev):
    ev_url = "v2/event/{}"
    teams_url = "v2/event/{}/teams"
    matches_url = "v2/event/{}/matches"

    events = []
    print "scraper init"
    event_doc = tba_call(ev_url, ev)
    print "event scraped"
    teams = tba_call(teams_url, ev)
    print "teams scraped"
    match_doc = tba_call(matches_url, ev)
    print "matches scraped"

    event_doc['teams'] = [ team(i['key']) for i in teams ]
    event_doc['matches'] = []
    print "teams processed"

    event = fms.Event(**event_doc)
    for i in event.teams:
        i.save()
    print "teams saved"
    event.save()
    print "event saved"
    matches(ev, match_doc)
    return event

def team(key):
    url = 'v2/team/{}'
    doc = tba_call(url, key)
    return fms.Team(**doc)

def cmp_match(match1, match2):
    if match1.comp_level == match2.comp_level:
        return cmp(match1.match_number, match2.match_number)
    else:
        return cmp(cmp_order.index(match1.comp_level), cmp_order.index(match2.comp_level))
cmp_order = ('p', 'q', 'ef', 'qf', 'sf', 'f')

def match_from_tba(tba_doc):
    tba_doc['red'] = tba_doc['alliances']['red']
    tba_doc['blue'] = tba_doc['alliances']['blue']
    tba_doc['event'] = tba_doc['event_key']
    tba_doc['comp_level'] = "q" if tba_doc["comp_level"] == "qm" else tba_doc["comp_level"]
    del tba_doc['alliances']
    return fms.Match(**tba_doc)

def matches(event, match_doc = None):
    print "match scraper init"
    url = 'v2/event/{}/matches'
    if match_doc is None:
        match_doc = tba_call(url, event)
    n=0
    matches = [ match_from_tba(doc) for doc in match_doc]
    for i in matches:
        i.save()
        n+=1
    e_db = fms.Event.objects.with_id(event)
    e_db.matches = sorted(matches, cmp=cmp_match)
    e_db.save()
    print "========= scraped %s matches =========" % n

def prct_mtch(num, red, blue):
    return {'comp_level': 'p', 'match_number': num, 'set_number': 1, 
        'key': '2014ilch_pm{}'.format(num), 'alliances': 
            {'blue': {'score': -1, 'teams': ["frc{}".format(i) for i in blue]}, 
            'red': {'score': -1, 'teams': ["frc{}".format(i) for i in red]}},
        'event_key': '2014ilch'}

practice_sched = [
    prct_mtch(1, [2062,2022,1739],[3352,2451,2704]),
    prct_mtch(2, [1739,2022,2062],[2704,2451,3352]),
    prct_mtch(3, [1739,2022,2062],[2704,2451,3352])
]

def scrp_prct():
    matches("2014ilch", [i.copy() for i in practice_sched])