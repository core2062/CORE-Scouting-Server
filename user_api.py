from helper import permission_required, check_args
from flask import request, g
from werkzeug import exceptions as ex

import model.user

def mix(app):
	@app.route('/user/account')
	@permission_required()
	def user_account():
		return g.user


	@app.route('/user/login', methods=['POST'])
	def user_login():
		"""get a token to use for authentication throughout the rest of the site"""
		#NOTE: no permission required for this part because it uses an alternative login method (username & password rather than token) and declares the user object on its own
		#CONSIDER: add a delay for password based login to prevent excessive attempts

		check_args(request.args, 'username', 'password')
		g.user = model.user.auth(request.args['username'], request.args['password'],
			ip=request.remote_addr)
		if not g.user:
			raise ex.Unauthorized('Bad username or password.')

		return {
			'notify': 'login successful',
			'token': g.user.token,
		}


	@app.route('/user/logout', methods=['POST'])
	@permission_required()
	def user_logout():
		g.user.logout()
		return {'notify': 'logout successful'}


	@app.route('/user/update', methods=['POST'])
	@permission_required()
	def user_update():
		raise ex.NotImplemented()


	@app.route('/user/signup', methods=['POST'])
	def signup():
		raise ex.NotImplemented()
		# try:
		# 	check_args(request.args, 'data')

		# 	user = User()
		# 	user.update(request.args['data'])
		# 	user.save()
		# except Exception as error:
		# 	return error_dump(error)

		return {'notify': 'signup successful'}

	@app.route('/debug/users')
	def listusers():
		model.user.defaults()
		return model.user.list_users()