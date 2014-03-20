
from flask import Flask, g, request, send_from_directory, render_template_string
from simplejson import loads

from model.db import database as db
import config
import views.beverages, views.commit, views.user, views.reports
import helper

class LocalFlask(Flask):
    jinja_options = {
        "extensions": ['jinja2.ext.autoescape', 'jinja2.ext.with_'],
        "trim_blocks": True,
        "lstrip_blocks": True
    }

app = LocalFlask(__name__)
app.jinja_env.filters['percent'] = helper.percent

app.secret_key = config.SECRET_KEY

app.register_blueprint(views.beverages.blueprint)
app.register_blueprint(views.commit.blueprint)
# app.register_blueprint(views.user.blueprint)
app.register_blueprint(views.reports.blueprint)

index_tmpl = """
    <style> @import url(http://fonts.googleapis.com/css?family=Orbitron:500);
    body {
        padding: 1.5em 3em;
    }
    h3 {
        font-family: Orbitron;
    }
    a {
        color: #ff731c;
        text-decoration: underline;
    }
    </style>
<h3><a href="/commit/submit/match">Submit a match scouting report</a></h3>
"""
@app.route("/")
def index():
    return render_template_string(index_tmpl)

@app.route('/matches.csv')
def make_csv():
    cols = data.keys()
    matches = db.commit.find({'match_type': 'q'}).sort('match_num')
    rows = []
    for match in matches:
        row = [None] * 30
        for k, v in match.items():
            if not k in cols:
                cols += [k]
            row[cols.index(k)] = v
        rows += [row]
    output = ''
    for line in ([cols] + rows):
        new_line = []
        for item in line:
            new_line += [str(item).replace(',', ';').replace('\r\n', '\n').replace('\n', ' | ')]
        output += ','.join(new_line) + '\n'
    open(app.config['CWD'] + 'matches.csv', 'w').write(output)
    return send_from_directory(app.config['CWD'], 'matches.csv')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
