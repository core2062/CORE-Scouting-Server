from flask import request, g
from werkzeug import exceptions as ex

from override_flask import make_json_app

from helper import check_args, permission_required
import model.db as db
from config import CURRENT_EVENT

app = make_json_app(__name__,)

# the limited public "guest" account is automatically used (by client) for most stuff that doesn't require much permission


@app.before_request
def before_request():
	# below stuff (g.notify & g.error) isn't really used... consider removing

	g.notify = []  # an array that holds notifications (like non-fatal errors or important messages)

	# a variable that holds an error... if there is one (there should be 1 or 0 errors returned)
	# a error is formatted as ('title','discription')
	#	title: one word name for the error
	#	description: text given to the user to tell what happened / how to fix
	g.error = ()


# @app.after_view
def after_view(rv):
	if not type(rv) in (dict, list):  # check to see that it's json, if not then return
		return
	#put stuff from g in response
	return

import user_api
user_api.mix(app)

@app.route('/')
def index():
	return """
		<!DOCTYPE html>
		<html>
			<head>
				<title>CSD</title>
			</head>
			<body>
				<p>put docs generated by sphinx here?</p>
			</body>
		</html>
	"""

#TODO: add mongs like db browser, with option to only return json (read only?) (restricted - not able to read user collection)

@app.route('/admin/reset',methods=['DELETE'])
@permission_required('reset_db')
def reset_db():
	db.clear()
	db.defaults()
	return {'200 OK': 'reset successful'}

@app.route('/coffee')
def coffee():
	raise ex.ImATeapot()	# I really agreed to this whole project just for an excuse to do this....

@app.route('/tea')
def tea():
	return '''
	                       (
            _           ) )
         _,(_)._        ((
    ___,(_______).        )
  ,'__.   /       \    /\_
 /,' /  |""|       \  /  /
| | |   |__|       |,'  /
 \`.|                  /
  `. :           :    /
    `.            :.,'
      `-.________,-'
'''


@app.route('/admin/scrape',methods=['POST'])
@permission_required()
def scrape():
	from scraper import scraper
	scraper.event_names()
	scraper.event_details()
	scraper.tpids()
	scraper.team_details()
	scraper.match(CURRENT_EVENT)
	return {'200 Ok':'Scrape successful'}

if __name__ == "__main__":
	app.run(
		debug=True,
	)
