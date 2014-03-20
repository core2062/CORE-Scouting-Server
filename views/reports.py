import flask
from werkzeug import exceptions as ex
from datetime import datetime
import analysis.event
import model.commit, model.team
from model.team import Team


blueprint = flask.Blueprint("analysis", __name__, url_prefix="/analysis")

@blueprint.route("/<e_key>/match/<key>")
def driver_report(e_key, key):
    
    teams = {
        "red1" : Team(2062, e_key),
        "red2" : Team(2062, e_key),
        "red3" : Team(2062, e_key),

        "blue1" : Team(2062, e_key),
        "blue2" : Team(2062, e_key),
        "blue3" : Team(2062, e_key),
    }
    return flask.render_template("driver_report.html", 
        teams=teams, date=datetime.now().strftime("%a %H:%M"), match=key, 
        reports=len(model.commit.MatchCommit.objects(event=e_key)))


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