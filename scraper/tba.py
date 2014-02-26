import requests
from model.log import log

h_id = {"X-TBA-App-Id": "core2062:scouting:dev"}
domain = "http://thebluealliance.com/api/"

def tba_call(endpoint, *args, **kwargs):
    r = requests.get(domain+(endpoint.format(*args)), headers=h_id, **kwargs)
    if not r.ok:
        log('error', "tba call error", str(r.status_code), endpoint)
        r.raise_for_status()
    return r.json

def events(year):
    list_url = "v1/events/list"
    ev_url = "v2/event/{}"
    teams_url = "v2/event/{}/teams"

    for ev in tba_call(list_url, params={"year": year}):
        event = tba_call(ev_url, ev['key'])
        teams = tba_call(teams_url, ev['key'])

        event['_teams'] = [ i['key'] for i in teams ]
        event['_id'] = event['key']; del event['key']
        event['_type'] = 'event'

        # print event;raw_input()
        yield event

def teams(year):
    # Get all teams attending an event, because TBA lacks a team list atm. 
    #  https://github.com/gregmarra/the-blue-alliance/issues/727
    from model.db import database as db
    url = 'v2/team/{}'
    teams = set()
    for event in db.fms.find({'_type': 'event', 'year': year}):
        teams.update(event['_teams'])
    l = len(teams)
    for i, team in enumerate(teams):
        t = tba_call(url, team)
        t['_id'] = t['key']; del t['key']
        t['_type'] = 'team'
        yield t
        if i%10 == 0:
            print "({} / {})".format(i, l)