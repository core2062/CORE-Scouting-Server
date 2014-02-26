import requests
import pytest
import simplejson as json


base = lambda x: 'http://localhost:5000' + str(x)

json_headers = {'content-type': 'application/json'}

##################
# User api tests
##################


@pytest.fixture
def login(scope="module"):
    loginParams = {'username': 'test-user', 'password': 'm3jhrk4'}
    login = requests.post(base('/user/login'), params=loginParams)
    token = login.json['token']
    assert token
    return token


def test_login():
    loginParams = {'username': 'test-user', 'password': 'm3jhrk4'}
    login = requests.post(base('/user/login'), params=loginParams)
    print login.status_code
    print login.json
    assert login.status_code == 200
    return login.json['token']


def test_accountDetails(login):
    acctParams = {'token': login}
    acct = requests.get(base('/user/account'), params=acctParams)
    # print acct.status_code
    print acct.text
    assert acct.json['name'] == 'test-user'
    assert acct.json['team'] == 0


def test_modify(login):
    from random import random

    newmail = 'newmail' + str(random())
    modifyData = json.dumps({'email': newmail, 'token': login})

    modify = requests.post(base('/user/update'), data=modifyData, headers=json_headers)

    print modify.status_code
    print modify.json
    assert modify.status_code == 200
    assert 'email' in modify.json['modified']

###################
# Commit api tests
###################


def test_schema():
    r = requests.get(base('/commit/schema'))
    print r.text
    assert r.status_code == 200
    assert r.json


def test_types():
    r = requests.get(base('/commit/types'))
    print r.text
    assert r.status_code == 200
    assert r.json


def test_type():
    r = requests.get(base('/commit/type/match'))
    print r.text
    assert r.status_code == 200
    assert r.json

# This should be filled in from json_schema...
match_data = {
    "match_num": 0,
    "team_num": 0,
    "match_type": "p",
    "alliance": "red",
    "auto_goal": False,
    "auto_hot": False,
    "auto_move": False,
    "auto_goalie": False,
    "auto_shots": 0,
    "cycles": 0,
    "total_cycles": 0,
    "truss_att": 0,
    "truss_made": 0,
    "catch_att": 0,
    "catch_made": 0,
    "high_att": 0,
    "high_made": 0,
    "low_att": 0,
    "low_made": 0,
    "pass": 0,
    "receive": 0,
    "block": 0,
    "percent_active": 0,
    "defense": "NO",
    "zones": "ALL",
    "gblocker": False,
    "pickup": False,
    "no_show": False,
    "yellow": 0,
    "red": 0,
    "fouls": 0,
    "tech_fouls": 0,
    "comments":""
}

commit_data = {
    "data": match_data,
    "data_type": "match"
}


def test_submission(login):
    d = commit_data.copy()
    d.update({'token': login})
    submit = requests.post(base('/commit/submit'), data=json.dumps(d), headers=json_headers)
    print submit.text
    assert submit.status_code == 200
    i = submit.json['id']
    c = requests.get(base('/commit/' + i))
    print c.text
    assert c.status_code == 200
    assert c.json == submit.json

if __name__ == '__main__':
    pytest.main('tests.py')
