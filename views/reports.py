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
    match = fms.Match.objects.with_id(e_key+"_"+key)
    for i in match.teams:
        i.calculate(e_key)
    return flask.render_template("driver_report.html", 
        red=match.red.teams, blue=match.blue.teams, date=datetime.now().strftime("%a %H:%M"), match=key, 
        reports=len(commit.MatchCommit.objects(event=e_key, match_type__ne="p")))

@blueprint.route("/<e_key>/commits")
def event_commits(e_key):
    scraper.tba.matches(e_key)
    event = fms.Event.objects.with_id(e_key)
    n = 0
    for match in event.matches:
        teams = set()
        in_match = [i.team_number for i in match.red.teams+match.blue.teams]
        if len(match.commits) > 6: print match.key, len(match.commits)
        for i in match.commits:
            if i.team in teams or (i.team not in in_match):
                # i.delete()
                print "removing commit for", i.team
            else:
                teams.add(i.team)
        match.team_commits = teams
        if 0 < len(match.team_commits) and len(match.team_commits) < 6:
            n+= 6-len(match.team_commits)
    return flask.render_template("event.html", event=event, n=n)

@blueprint.route("/<e_key>/teams")
def team_data(e_key):
    teams = []
    event = fms.Event.objects.with_id(e_key)
    columns = (
        ("team_number", "Team"),
        ("avg_contrib", "Contribution"),
        ("avg_auto_contrib", "Autonomous Contrib"),
        ("avg_high", "High Goals"),
        ("avg_truss", "Truss Made"),
        ("avg_inbound", "Inbounds"),
        ("avg_team_cycles", "Team Cycles"),
        ("sum_disabled", "Total Disabled Matches"),
        ("sum_red", "Total Red Cards"),
        ("avg_foul_contrib", "Foul Contribution")
    )
    print "Starting team calculations..."
    for team in event.teams:
        team.calculate(e_key)
        teams.append([(name, getattr(team, key)) for key, name in columns])
    output = ""
    output+=", ".join(i[1] for i in columns)
    output+="\n"
    for team in teams:
        output += ", ".join(str(i[1]) for i in team) + "\n"
    response = flask.make_response(output)
    response.headers["content-type"] = "text/plain"
    return response


other_teams_tmpl = """
<h2> Regionals to watch results for {{event}} </h2>
There are {{total}} teams at this regional.
{{loners}} teams are only attending the one regional.
Here is the breakdown for the remaining {{total - loners}}:

{% for i in regionals %}
<h3><a href="http://thebluealliance.com/event/{{i.key}}">{{ i.name }}</a> 
{{i.date.month}}/{{i.date.day}} ({{i.n_teams}} team{{"s" if i.n_teams > 1 else ""}} in common)</h3>
{{i.team_str}}

{% endfor %}"""
@blueprint.route("/<e_key>/other_teams.html")
def event_html(e_key):
    try:
        return flask.render_template_string(other_teams_tmpl, **analysis.event.regionals_to_watch(e_key))
    except ValueError, e:
        return ex.NotFound("Event {} not found.".format(e_key))