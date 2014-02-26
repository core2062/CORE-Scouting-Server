from werkzeug import exceptions as ex
import model.commit
import model.match
from helper import permission_required, allow_origins
#from jsonschema import ValidationError
import flask

"""api used for submitting commits"""

blueprint = flask.Blueprint("commits", __name__, url_prefix="commit")

@blueprint.route('/submit', methods=["POST"])
@allow_origins
@permission_required()
def submit_commit():
    a = flask.g.args.copy()
    del a['token']
    return model.commit.commit(flask.g.user, a)

@blueprint.route('/schema')
def schema():
    return model.commit.wrapper_schema

@blueprint.route('/types')
def types():
    return model.commit.types

@blueprint.route('/type/<data_type>')
def data_schema(data_type):
    if data_type not in model.commit.types:
        raise ex.NotFound("No data type %s. See /commit/types for a list of data types." % data_type)
    else:
        return getattr(model.commit, data_type + "_schema")

@blueprint.route('/<commit>')
def get_commit(commit):
    c = model.commit.Commit(commit)
    if not c:
        raise ex.NotFound('No commmit ' + commit)
    return c

#   @app.route('/match/<match_type>/<match_num>')
#   def get_match():
#       return Match(match_type, match_num)
