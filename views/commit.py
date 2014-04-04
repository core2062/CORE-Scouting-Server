from werkzeug import exceptions as ex
import simplejson as json
import flask
import wtforms_me
import wtforms.fields

import model.commit
import config

"""api used for submitting commits"""

blueprint = flask.Blueprint("commits", __name__, url_prefix="/commit")

MatchForm = wtforms_me.model_form(model.commit.MatchCommit)
MatchForm.event = wtforms.fields.HiddenField(**MatchForm.event.kwargs)
@blueprint.route('/submit', methods=["GET","POST"])
def submit_commit():
    form = MatchForm(flask.request.form)
    if flask.request.method == "POST" and form.validate():
        form.save()
        flask.flash('Thanks for your submission! <a href="/commit/{}">Edit it &mdash;></a>'
            .format(form.instance.key))
        return flask.redirect("/commit/submit")
    return flask.render_template('commit_submit.html', form=form, type="match")

@blueprint.route('/', methods=["GET","POST"])
def commit_search():
    query = {"event":config.event, "match_type":'q'}
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


@blueprint.route('/<cid>', methods=["GET","POST"])
def get_commit(cid):
    try:
        c = model.commit.get_commit(cid)
        e_key, match_type, match_num, team = model.commit.parse_cid(cid)
        obj = {"event":e_key, "match_type":match_type, "match_num": match_num, "team": team}
        print c
        form = MatchForm(flask.request.form, instance=c) if c else MatchForm(flask.request.form, **obj)
    except ValueError:
        raise ex.BadRequest("Commit id %s malformatted." % cid)
    if flask.request.method == "POST" and form.validate():
        if c: print c; c.delete()
        form = MatchForm(flask.request.form)
        form.save()
        flask.flash("Thanks for your submission!")
        return flask.redirect("/commit/submit")
    return flask.render_template("commit_submit.html", form=form, type="match", furl=flask.request.url)
