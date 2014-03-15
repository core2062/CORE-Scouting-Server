import requests
import pytest
import simplejson as json
import jsonhelper


base = lambda x: 'http://localhost' + str(x)

json_headers = {'content-type': 'application/json'}

##################
# User api tests
##################


@pytest.fixture
def login(scope="module"):
    loginParams = {'username': 'test-user', 'password': 'm3jhrk4'}
    login = requests.post(base('/user/login'), params=loginParams)
    token = login.json()['token']
    assert token
    return token


def test_login():
    loginParams = {'username': 'test-user', 'password': 'm3jhrk4'}
    login = requests.post(base('/user/login'), params=loginParams)
    # print login.status_code
    # print login.json()
    assert login.status_code == 200
    return login.json()['token']


def test_accountDetails(login):
    acctParams = {'token': login}
    acct = requests.get(base('/user/account'), params=acctParams)
    # print acct.status_code
    print acct.text
    assert acct.json()['name'] == 'test-user'
    assert acct.json()['team'] == 0


def test_modify(login):
    from random import random

    newmail = 'newmail' + str(random())
    modifyData = json.dumps({'email': newmail, 'token': login})

    modify = requests.post(base('/user/update'), data=modifyData, headers=json_headers)

    # print modify.status_code
    # print modify.json
    assert modify.status_code == 200
    assert 'email' in modify.json()['modified']

###################
# Commit api tests
###################

@pytest.fixture
def schema():
    return json.loads(jsonhelper.remove_comments(open('schema/match.schema.json').read()))

@pytest.fixture
def schema_defaults(scope="module"):
    defaults = {
        "match_num": 1,
        "team": 2062,
        "match_type": "p",
        "scout": "xxBADxx"
    }
    x = schema()
    return { k: (v['default'] if 'default' in v else defaults[k]) for k, v in x.iteritems() }

def test_schema(schema):
    r = requests.get(base('/commit/type/match'))
    assert r.status_code == 200
    assert r.json()
    assert r.json() == schema


def test_types():
    r = requests.get(base('/commit/types'))
    assert r.status_code == 200
    assert r.json()


def test_type():
    r = requests.get(base('/commit/type/match'))
    assert r.status_code == 200
    assert r.json()

def test_submission(login, schema_defaults):
    d = schema_defaults.copy()
    d.update({'token': login})
    submit = requests.post(base('/commit/submit/match'), data=json.dumps(d), headers=json_headers)
    assert submit.status_code == 200
    # print submit.json()
    commit = submit.json()
    i = commit['_id']["$oid"]
    c = requests.get(base('/commit/' + i))
    assert c.status_code == 200
    # assert c.json() == submit.json()
    ret = c.json()
    flag = True
    for k, v in ret.iteritems():
        if not k in commit:
            print "%s (%s) new in returned commit" % (k, v)
            # flag = False
        elif v != commit[k]:
            print "%s differs in returned commit (%s / %s) " % (k, v, commit[k])
            flag = False
    for k, v in commit.iteritems():
        if not k in ret:
            print "%s (%s) missing in returned commit" % (k, v)
            flag = False
    assert flag

if __name__ == '__main__':
    pytest.main('tests.py')
