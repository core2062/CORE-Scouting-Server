import requests
import sys

def die(message):
	print message
	sys.exit()

base=lambda x:'http://localhost:5000/'+str(x)

loginParams={'username':'test-user','password':'m3jhrk4'}
login = requests.post(base('user/login'), params=loginParams)
print login.status_code
print login.json
if login.status_code != 200:
	die('Error in login')

token = login.json['token']

acctParams = {'token':token}
acct = requests.get(base('user/account'), params=acctParams)
print acct.status_code
print acct.text