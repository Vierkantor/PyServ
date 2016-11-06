from flask import session

import base_test
from test_login import login

from pyserv.auth import set_shadow_user
from pyserv.database import db
from pyserv.person import User, get_logged_in

def shadow_user(client, user_id):
	return client.post('/service/shadow_user',
		data={
			'user_id': user_id,
		},
		follow_redirects=True,
	)

def test_shadow_auth(client):
	"""Shadowing requires god auth."""
	response = shadow_user(client, -1)
	assert response.status_code == 403

def test_shadow_invalid(client, god_user):
	"""Shadowing an invalid user id simply makes you not shadowing."""
	god = god_user()
	assert b'You were logged in' in login(client, god.nickname, "").data
	response = shadow_user(client, -1)
	assert response.status_code == 200
	assert 'shadow_user' not in session

def test_shadow_valid(client, god_user, test_user):
	"""Shadowing a user makes them the current_user and you the shadow_user."""
	god = god_user()
	test = test_user()
	assert b'You were logged in' in login(client, god.nickname, "").data
	response = shadow_user(client, test.id)
	assert response.status_code == 200
	assert session['current_user'] == test.id
	assert session['shadow_user'] == god.id
	assert get_logged_in() == test

def test_shadow_replace(client, god_user, test_user):
	"""Shadowing a user when already shadowing should work the same as unshadowing and reshadowing."""
	god = god_user()
	test1 = test_user()
	assert b'You were logged in' in login(client, god.nickname, "").data
	assert shadow_user(client, test1.id).status_code == 200
	test2 = test_user()
	response = shadow_user(client, test2.id)
	assert response.status_code == 200
	assert session['current_user'] == test2.id
	assert session['shadow_user'] != test1.id
	assert session['shadow_user'] == god.id
	assert get_logged_in() == test2

