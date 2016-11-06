from flask import session

import base_test
from test_login import login

from pyserv.auth import has_auth

def create_key(client):
	return client.post('/service/api_key/create',
		follow_redirects=True,
	)

def check_auth(client, api_key, auth_level):
	response = client.get('/',
		data={
			'api_key': api_key,
		},
	)
	assert has_auth(auth_level)
	return response

def test_make_api_key(client, test_user):
	"""Give the client an api key."""
	test = test_user()
	assert b'You were logged in' in login(client, test.nickname, "").data
	response = create_key(client)
	assert b'Created key' in response.data
