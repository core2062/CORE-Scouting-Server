from werkzeug import exceptions as ex
from jsonschema import ValidationError
import flask; from flask import g

from helper import permission_required, allow_origins
import model.commit
import model.match
"""api used for submitting commits"""

blueprint = flask.Blueprint("commits", __name__, url_prefix="/commit")

@blueprint.route('/submit/<ctype>', methods=["POST"])
@allow_origins
def submit_commit(ctype):
    if not ctype in model.commit.types:
        return ex.NotFound("Type must be one of ("+", ".join(model.commit.types)+")")
    raw = dict()
    print g.args
    for i in model.commit.types[ctype]:
        raw[i] = g.args[i] if i in g.args else None
    print raw
    try:
        model.commit.validate_data_type(ctype, raw)
    except ValidationError, e:
        raise ex.BadRequest(
            "Doesn't match %s schema. See /commit/type/%s for a copy. %s" 
            % (ctype, ctype, str(e))
        )
    commit = model.commit.Commit(**raw)
    if flask.g.get('user', None) is not None:
        commit.user = flask.g.user.oi
    else:
        commit.user = None
    commit.save()
    return commit.to_json()

@blueprint.route('/types')
@allow_origins
def types():
    return model.commit.types

@blueprint.route('/type/<data_type>')
@allow_origins
def data_schema(data_type):
    print data_type
    if data_type not in model.commit.types:
        raise ex.NotFound("No data type %s. See /commit/types for a list of data types." % data_type)
    else:
        return model.commit.types[data_type]

@blueprint.route('/<commit>')
@allow_origins
def get_commit(commit):
    c = model.commit.Commit.objects.with_id(commit)
    if not c:
        raise ex.NotFound('No commmit ' + commit)
    return c.to_json()

#   @app.route('/match/<match_type>/<match_num>')
#   def get_match():
#       return Match(match_type, match_num)
