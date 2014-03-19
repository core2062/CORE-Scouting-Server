import requests
import pytest
import simplejson as json
import jsonhelper


base = lambda x: 'http://localhost' + str(x)

@pytest.fixture
def login(scope="module"):
    loginParams = {'username': 'test-user', 'password': 'm3jhrk4'}
    login = requests.post(base('/user/login'), params=loginParams)
    token = login.json()['token']
    assert token
    return token

def login():
    pass


###################
# Commit api tests
###################

@pytest.fixture
def submit_defaults(scope="module"):
    return {
        "match_num": 1,
        "team": 2062,
        "match_type": "p",
        "scout": "xxBADxx"
    }

def test_submission(submit_defaults):
    args = schema_defaults.copy()
    page = requests.get(base('/commit.submit/match'))
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
