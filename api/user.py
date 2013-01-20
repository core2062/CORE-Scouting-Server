from helper import permission_required, check_args
from flask import request, g
from werkzeug import exceptions as ex

from model.user import password_auth, new_user


def mix(app):
	@app.route('/user/account')
	@permission_required()
	def self_account():
		return g.user

	@app.route('/user/login', methods=['POST'])
	def user_login():
		"""get a token to use for authentication throughout the rest of the site"""
		#NOTE: no permission required for this part because it uses an
		#alternative login method (username & password rather than token) and
		#declares the user object on its own

		#CONSIDER: add a delay for password based login to prevent excessive attempts

		check_args(g.args, 'username', 'password')
		g.user = password_auth(g.args['username'], g.args['password'],
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
	def user_update_self():
		g.user.update(g.args['data'])
		return {'notify': 'update successful'}

	@app.route('/user/signup', methods=['POST'])
	@permission_required('make-user')
	def signup():
		check_args(request.json, 'name', 'password')
		new_user(g.args['data'])
		return {'notify': 'signup successful'}

# might need this stuff later, but if we're going with a simplistic admin CLI,
# we won't need it for awhile
#
# 	@app.route('/users/<user>')
# 	def user_account(user):
# 		return exUser(user)

# 	@app.route('/user/update/<user>', methods=['POST'])
# 	@permission_required('modify-other')
# 	def user_update_other(user):
# 		modified = []
# 		for i in model.user.User.public_attrs:
# 			if i in request.json.keys():
# 				g.user.raw += {i: request.json[i]}
# 				modified.append(i)

# 		return {'notify': 'Update successful', 'modified': modified}

# 	@app.route('/users/<user>/delete', methods=['DELETE'])
# 	@permission_required('remove-user')
# 	def remove_user(user):
# 		"""
# 		"""
# 		#u = exUser(user)

# 	@app.route('/debug/users')
# 	def listusers():
# 		model.user.defaults()
# 		return model.user.list_users()


# def exUser(user):
# 	try:
# 		return model.user.User(user)
# 	except ValueError:
# 		raise ex.NotFound('User ' + user + ' not found')
