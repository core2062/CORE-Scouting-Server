import requests
from operator import attrgetter

from model.log import log
from model.db import database as db
from model import fms

h_id = {"X-TBA-App-Id": "core2062:scouting:2014wimi"}
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
    event_doc = tba_call(ev_url, ev)
    teams = tba_call(teams_url, ev)
    matches = tba_call(matches_url, ev)

    event_doc['teams'] = [ team(i['key']) for i in teams ]
    event_doc['matches'] = [ fms.match_from_tba(doc) for doc in matches]

    event = fms.Event(**event_doc)
    for i in event.teams:
        i.save()
    event.save()
    matches(ev)
    return event

def team(key):
    doc = db.fms.find_one(key)
    doc['key'] = ['_id']
    return fms.Team(**doc)

def cmp_match(match1, match2):
    if match1.comp_level == match2.comp_level:
        return cmp(match1.match_number, match2.match_number)
    else:
        return cmp(cmp_order.index(match1.comp_level), cmp_order.index(match2.comp_level))
cmp_order = ('qm', 'ef', 'qf', 'sf', 'f')

def matches(event):
    print "SCRAPER INIT"
    url = 'v2/event/{}/matches'
    match_doc = tba_call(url, event)
    n=0
    matches = [ fms.match_from_tba(doc) for doc in match_doc]
    for i in matches:
        i.save()
        n+=1
    e_db = fms.Event.objects.with_id(event)
    e_db.matches = sorted(matches, cmp=cmp_match)
    e_db.save()
    print "========= SCRAPED %s MATCHES =========" % n

if __name__ == '__main__':
    matches("2014wimi")