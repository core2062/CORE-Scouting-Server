import flask

import analysis
from config import jinja_env
from werkzeug import exceptions as ex

blueprint = flask.Blueprint("analysis", __name__, url_prefix="analysis")

@blueprint.route("/event/<key>/other_teams")
def event_json(key):
	try:
		return analysis.event.regionals_to_watch(key)
	except ValueError, e:
		return ex.NotFound("Event {} not found.".format(key))

other_teams_tmpl = jinja_env.from_string("""
<h2> Regionals_to_watch results for {{event}} </h2>
There are {{total}} teams at this regional.
{{loners}} teams are only attending the one regional.
Here is the breakdown for the remaining {{total - loners}}:

{% for i in regionals %}
<h3><a href="https://thebluealliance.com/events/{{i.key}}">{{ i.name }}</a> 
{{i.date.month}}/{{i.date.day}} ({{i.n_teams}} team{{"s" if i.n_teams > 1 else ""}} in common)</h3>
{{i.team_str}}

{% endfor %}""")
@blueprint.route("/event/<key>/other_teams.html")
def event_html(key):
	try:
		return other_teams_tmpl.render(analysis.event.regionals_to_watch(key))
	except ValueError, e:
		return ex.NotFound("Event {} not found.".format(key))