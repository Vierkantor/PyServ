from flask import session

import base_test

from pyserv.auth import has_auth, levels
from pyserv.database import db
from pyserv.person import User, get_login, get_logged_in

def login(client, username, password):
	return client.post('/service/login',
		data={
			'user': username,
			'pass': password,
		},
		follow_redirects=True,
	)

def ensure_logged_in(client, user):
	"""Log in as the given user.

	The user must be made by one of the test_user factories, e.g. god_user.
	Otherwise, the password is inaccessible because storing plaintext passwords is a Bad Thing.
	"""
	response = login(client, user.nickname, user._actual_password)
	base_test.check_response(response)
	assert b'You were logged in' in response.data
	return response

def logout(client):
	return client.get('/service/logout',
		follow_redirects=True,
	)
def test_invalid_credentials(client):
	"""What happens when you provide the wrong login data?"""
	assert b'Invalid credentials' in login(client, 'invalid', 'data').data
def test_login_gives_auth(client):
	test_user = User(full_name="Login Test User", nickname="test_login_gives_auth", password="user")
	db.session.add(test_user)
	db.session.commit()
	assert get_login('test_login_gives_auth', 'user') is not None
	assert b'You were logged in' in login(client, 'test_login_gives_auth', 'user').data
	assert session['current_user'] == test_user.id
	assert get_logged_in() == test_user
	assert has_auth(levels.logged_in)
	assert b'You were logged out' in logout(client).data
	assert not has_auth(levels.logged_in)
