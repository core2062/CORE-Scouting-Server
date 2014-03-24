from werkzeug import exceptions as ex
import simplejson as json
import flask
import wtforms_me
import wtforms.fields

import model.commit
"""api used for submitting commits"""

blueprint = flask.Blueprint("commits", __name__, url_prefix="/commit")

MatchForm = wtforms_me.model_form(model.commit.MatchCommit)
MatchForm.event = wtforms.fields.HiddenField(**MatchForm.event.kwargs)
@blueprint.route('/submit', methods=["GET","POST"])
def submit_commit():
    form = MatchForm(flask.request.form)
    if flask.request.method == "POST" and form.validate():
        form.save()
        flask.flash("Thanks for your submission!")
        return flask.redirect("/commit/submit")
    return flask.render_template('commit_submit.html', form=form, type="match")

@blueprint.route('/', methods=["GET","POST"])
def commit_search():
    query = {"event":"2014wimi", "match_type":'q'}
    errors = []
    if flask.request.method == "POST" and flask.request.form.get("query", None):
        try:
            query = json.loads(flask.request.form.get("query"))
        except Exception, e:
            print e
            errors.append(e.message)
    objects = []
    try:
        objects = list(model.commit.MatchCommit.objects(**query).order_by("-time"))
    except Exception, e:
        print e
        errors.append(e.message)
    return flask.render_template("commit_search.html", objects=objects,
        query=json.dumps(query), errors=errors)


@blueprint.route('/<cid>')
def get_commit(cid):
    cid = cid.split("_")
    try:
        e_key, match, team = cid
        match_type, match_num = match.split("m")
    except:
        return ex.NotFound("Commit id malformated.")
    c = model.commit.Commit.objects(event=e_key, match_num=match_num, match_type=match_type)
    if not c:
        raise ex.NotFound('No commmit ' + match)
    return flask.render_template("commit.html")
