import flask
from werkzeug import exceptions as ex
from datetime import datetime
import itertools

import analysis.event
from model import fms, commit
import scraper.tba

blueprint = flask.Blueprint("reports", __name__, url_prefix="/reports")

@blueprint.route("/<e_key>/match/<key>")
def driver_report(e_key, key):
    if 'm' not in key and 'f' not in key:
        l = list(key)
        l.insert(1,'m')
        key = ''.join(l)
    if 'f' in key and 'm' not in key:
        key+='m1'
    print key
    match = fms.Match.objects.with_id(e_key+"_"+key)
    print e_key
    print match
    for i in match.teams:
        i.calculate(e_key)
    return flask.render_template("driver_report.html", 
        red=match.red.teams, blue=match.blue.teams, date=datetime.now().strftime("%a %H:%M"), match=key, 
        reports=len(commit.MatchCommit.objects(event=e_key, match_type="q")))

@blueprint.route("/<e_key>/commits")
def event_commits(e_key):
    scraper.tba.matches(e_key)
    event = fms.Event.objects.with_id(e_key)
    n = 0
    for match in event.matches:
        match.team_commits = set(i.team_number for i in match.teams if
                bool(sum([n.team == i.team_number for n in match.commits])))
        if 0 < len(match.team_commits) and len(match.team_commits) < 6:
            # print len(match.team_commits)
            n+= 6-len(match.team_commits)
    return flask.render_template("event.html", event=event, n=n)

other_teams_tmpl = """
<h2> Regionals_to_watch results for {{event}} </h2>
There are {{total}} teams at this regional.
{{loners}} teams are only attending the one regional.
Here is the breakdown for the remaining {{total - loners}}:

{% for i in regionals %}
<h3><a href="https://thebluealliance.com/events/{{i.key}}">{{ i.name }}</a> 
{{i.date.month}}/{{i.date.day}} ({{i.n_teams}} team{{"s" if i.n_teams > 1 else ""}} in common)</h3>
{{i.team_str}}

{% endfor %}"""
@blueprint.route("/event/<key>/other_teams.html")
def event_html(key):
    try:
        return flask.render_template_string(analysis.event.regionals_to_watch(key))
    except ValueError, e:
        return ex.NotFound("Event {} not found.".format(key))