import os
from copy import copy

from flask import g, request, send_from_directory
from simplejson import loads

from model.db import database as db
from helper import allow_origins, check_args
import api.beverages
import api.commit
import api.user
import api.analysis
from config import app

app.register_blueprint(api.beverages.blueprint)
app.register_blueprint(api.commit.blueprint)
app.register_blueprint(api.user.blueprint)
app.register_blueprint(api.analysis.blueprint)

@app.before_request
def before_request():
    # put the request args in a mutable dict so we can pre-process them
    g.args = dict(request.args.to_dict())
    # if POST args or json are sent, merge that into the args
    if request.json:
        g.args.update(request.json)
    if request.form:
        g.args.update(request.form.to_dict())

    # below stuff (g.notify & g.error) isn't really used... consider removing
    # an array that holds notifications (like non-fatal errors or important messages)
    #g.notify = []


# @app.after_view
# def after_view(rv):
#   # check to see that it's json, if not then return
#   if not type(rv) in (dict, list):
#       return
#   #put stuff from g in response
#   return

@app.route('/matches.csv')
def make_csv():
    cols = data.keys()
    matches = db.scouting.find({'match_type': 'q'}).sort('match_num')
    rows = []
    for match in matches:
        del match['_id']
        try:
            del match['auto_pyramid']
        except:
            pass
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
