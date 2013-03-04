from helper import permission_required, check_args
from flask import request, g
from werkzeug import exceptions as ex

import model.user
import model.commit


def mix(app):
	@app.route('/user/account')
	@permission_required()
	def self_account():
		return g.user

	@app.route('/user/<user>')
	def user_account(user):
		return exUser(user)

	@app.route('/user/account/commits')
	def self_commits():
		return model.commit.by_user(g.user)

	@app.route('/user/<user>/commits')
	def user_commits():
		if not model.user.exists(user):
			raise ex.NotFound("No user "+user)
		return model.commit.by_user(user)

	@app.route('/user/login', methods=['POST'])
	def user_login():
		"""get a token to use for authentication throughout the rest of the site"""
		#NOTE: no permission required for this part because it uses an
		#alternative login method (username & password rather than token)
		#and declares the user object on its own
		#CONSIDER: add a delay for password based login to prevent excessive attempts

		check_args('username', 'password')
		print g.args
		g.user = model.user.auth(g.args['username'], g.args['password'],
			ip=request.remote_addr)
		if not g.user:
			raise ex.Unauthorized('Bad username or password.')

		return {
			'message': 'login successful',
			'token': g.user.token,
		}

	@app.route('/user/logout', methods=['POST'])
	@permission_required()
	def user_logout():
		g.user.logout()
		return {'message': 'logout successful'}

	@app.route('/user/update', methods=['POST'])
	@permission_required()
	def user_update_self():
		modified = []
		for i in g.user.public_attrs:
			if i in g.args.keys():
				g.user.raw += {i: g.args[i]}
				modified.append(i)
		return {'message': 'Update successful', 'modified': modified}

	@app.route('/user/update/<user>', methods=['POST'])
	@permission_required('modify-other')
	def user_update_other(user):
		#other = exUser(user)

		modified = []
		for i in model.user.User.public_attrs:
			if i in g.args.keys():
				g.user.raw += {i: g.args[i]}
				modified.append(i)

		# if g.user.has_perm('modify-perm'):
		# 	if 'perms' in request.json.keys:
		# 		if
		# 		other.perms +=
		return {'message': 'Update successful', 'modified': modified}

	@app.route('/user/signup', methods=['POST'])
	@permission_required('make-user')
	def signup():
		check_args(g.args, 'name', 'password')
		u = model.user.new_user(
			g.args['name'],
			g.args['password'],
			g.args)
		return {'message': 'signup successful', 'user': u}

	# @app.route('/users/<user>/delete', methods=['DELETE'])
	# @permission_required('remove-user')
	# def remove_user(user):
	# 	"""Remove user"""
	# 	pass
	# 	# u = exUser(user)
def exUser(user):
	try:
		return model.user.User(user)
	except ValueError:
		raise ex.NotFound('User ' + user + ' not found')