import requests
import pytest
import simplejson as json


base = lambda x: 'http://localhost:5000' + str(x)

json_headers = {'content-type': 'application/json'}


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

#edit this before the season starts

match_data = {
	"match_num": 0,
	"team_num": 0,
	"match_type": "p",
	"alliance": "red",
	"auto_goal": false,
	"auto_hot": false,
	"auto_move": false,
	"auto_goalie": false
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
	"zones": "ALL"
	"gblocker": false,
	"pickup": false,
	"no_show": false,
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
