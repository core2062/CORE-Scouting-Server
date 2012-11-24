import requests
import sys
from random import random
import simplejson as json
import pytest

def die(message):
	print message
	sys.exit()

base=lambda x:'http://localhost:5000/'+str(x)

@pytest.fixture
def login():
	loginParams={'username':'test-user','password':'m3jhrk4'}
	login = requests.post(base('user/login'), params=loginParams)
	token = login.json['token']
	assert token
	return token

def test_login():
	loginParams={'username':'test-user','password':'m3jhrk4'}
	login = requests.post(base('user/login'), params=loginParams)
	print login.status_code
	print login.json
	assert login.status_code == 200

def test_accountDetails(login):
	acctParams = {'token':login}
	acct = requests.get(base('user/account'), params=acctParams)
	# print acct.status_code
	print acct.text
	assert acct.json['name']=='test-user'
	assert acct.json['team']==0

def test_modify(login):
	newmail='newmail'+str(random())
	modifyData = json.dumps({'email':newmail,'token':login})
	modifyHeaders= {'content-type': 'application/json'}
	modify = requests.post(base('user/update'), data=modifyData, headers=modifyHeaders)
	print modify.status_code
	print modify.json
	assert modify.status_code == 200
	assert 'email' in modify.json['modified']