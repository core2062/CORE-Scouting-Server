from helper import permission_required, check_args
import flask; from flask import request, g
from werkzeug import exceptions as ex
    
import model
from model import user, commit
from helper import allow_origins

blueprint = flask.Blueprint("users", __name__, url_prefix="/user")

@blueprint.route('/account')
@permission_required()
def self_account():
    return g.user.to_dict()

@blueprint.route('/<user>')
def user_account(user):
    return exUser(user).to_dict()

@blueprint.route('/account/commits')
def self_commits():
    return commit.by_user(g.user).to_dict()

@blueprint.route('/<user>/commits')
def user_commits():
    if not model.user.exists(user):
        raise ex.NotFound("No user " + user)
    return commit.by_user(user)

@blueprint.route('/login', methods=['POST'])
@allow_origins
def user_login():
    """get a token to use for authentication throughout the rest of the site"""
    #NOTE: no permission required for this part because it uses an
    #alternative login method (username & password rather than token)
    #and declares the user object on its own
    #CONSIDER: add a delay for password based login to prevent excessive attempts

    check_args('username', 'password')
    g.user = user.auth(g.args['username'], g.args['password'],
        ip=request.remote_addr)
    if not g.user:
        raise ex.Unauthorized('Bad username or password.')

    return {
        'message': 'login successful',
        'token': g.user.token,
    }

@blueprint.route('/logout', methods=['POST'])
@permission_required()
def user_logout():
    g.user.logout()
    return {'message': 'logout successful'}

@blueprint.route('/update', methods=['POST'])
@permission_required()
def user_update_self():
    modified = []
    for i in g.user.public_attrs:
        if i in g.args.keys():
            g.user.raw += {i: g.args[i]}
            modified.append(i)
    return {'message': 'Update successful', 'modified': modified}

@blueprint.route('/update/<user>', methods=['POST'])
@permission_required('modify-other')
def user_update_other(user):
    #other = exUser(user)

    modified = []
    for i in user.User.public_attrs:
        if i in g.args.keys():
            g.user.raw += {i: g.args[i]}
            modified.append(i)

    # if g.user.has_perm('modify-perm'):
    #   if 'perms' in request.json.keys:
    #       if
    #       other.perms +=
    return {'message': 'Update successful', 'modified': modified}

@blueprint.route('/signup', methods=['POST'])
@permission_required('make-user')
def signup():
    check_args(g.args, 'name', 'password')
    u = user.new_user(
        g.args['name'],
        g.args['password'],
        g.args)
    return {'message': 'signup successful', 'user': u}

# @blueprint.route('/users/<user>/delete', methods=['DELETE'])
# @permission_required('remove-user')
# def remove_user(user):
#   """Remove user"""
#   pass
#   # u = exUser(user)


def exUser(user):
    try:
        return user.User(user)
    except ValueError:
        raise ex.NotFound('User ' + user + ' not found')
