from werkzeug import exceptions as ex
import simplejson as json
import flask
import wtforms_me

import model.commit
"""api used for submitting commits"""

blueprint = flask.Blueprint("commits", __name__, url_prefix="/commit")

MatchForm = wtforms_me.model_form(model.commit.MatchCommit)
@blueprint.route('/submit/match', methods=["GET","POST"])
def submit_commit():
    form = MatchForm(flask.request.form)
    if flask.request.method == "POST" and form.validate():
        form.save()
        flask.flash("Thanks for your submission!")
        return flask.redirect("/commit/submit/match")
    return flask.render_template('commit.html', form=form, type="match")

@blueprint.route('/show', methods=["GET","POST"])
def commit_search():
    query = {}
    errors = []
    if flask.request.method == "POST" and flask.request.form.get("query", None):
        try:
            query = json.loads(flask.request.form.get("query"))
        except Exception, e:
            print e
            errors.append(e.message)
    objects = []
    try:
        objects = list(model.commit.MatchCommit.objects(**query))
    except Exception, e:
        print e
        errors.append(e.message)
    return flask.render_template("commit_search.html", objects=objects,
        query=json.dumps(query), errors=errors)


# @blueprint.route('/<match>')
# def get_commit(match):
#     c = model.commit.Commit.objects.with_id(match)
#     if not c:
#         raise ex.NotFound('No commmit ' + match)
#     return c.to_json()


#   @app.route('/match/<match_type>/<match_num>')
#   def get_match():
#       return Match(match_type, match_num)
