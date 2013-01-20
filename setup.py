#this doesn't really belong here, but it's setup related
def defaults():
	user = new_user("admin", 'mApru', fullname='Kai\'ckul')
	user.give_perm("*")
	user = new_user('test-user', 'm3jhrk4')