import requests

base=lambda x:'http://localhost:5000/'+str(x)

loginParams={'username':'test-user','password':'m3jhrk4'}
login = requests.get(base('user/login'), params=loginParams)
print login.status_code
print login.json

token = login.json['token']

acctParams = {'token':token}
acct = requests.get(base('user/account'), params=acctParams)
print acct.status_code
print acct.text