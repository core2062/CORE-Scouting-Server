
from collections import defaultdict
from datetime import datetime

from model.db import database as db
from model.log import log

date_format = "%Y-%m-%dT%H:%M:%S"

def regionals_to_watch(event_key):
    n = db.fms.find_one(event_key)
    if not n:
        raise ValueError("No event "+event_key)
    teams = n["_teams"]
    data = {}
    data["total"] = len(teams)
    data["event"] = n["name"]
    other_events = defaultdict(list)
    event_data = set()
    loners = 0
    for j in teams:
        t = db.fms.find_one(j)
        if not t:
            log.error("No team {} found in database!".format(i)); continue
        if len(t["events"]) == 1:
            loners += 1
        else:
            for i in t["events"]:
                k = i["key"]
                if k != event_key:
                    other_events[k].append(t)
                    event_data.add((k, datetime.strptime(i['start_date'], date_format), i['name']))
    data['loners'] = loners
    data['regionals'] = []
    sorted_ev = sorted(event_data, key=lambda x: x[1])
    for key, date, name in sorted_ev:
        tms = other_events[key]
        data['regionals'].append({
            'key': key,
            'date': date,
            'name': name,
            'n_teams': len(tms),
            'team_str': ", ".join(i['nickname'] + 
                " ({})".format(i['team_number']) for i in tms)
        })
    return data