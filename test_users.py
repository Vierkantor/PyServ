import base_test

from pyserv.database import db
from pyserv.person import User

def user_profile(client, user_id):
	return client.get('/user/{}'.format(user_id),
		follow_redirects=True,
	)

def test_view_user_profile(client, test_user):
	"""View a basic user profile."""
	user = test_user()
	assert bytes(user.full_name, encoding='utf-8') in user_profile(client, user.id).data

def test_view_nonexistent_user(client):
	"""View the profile of a user who doesn't exist."""
	assert user_profile(client, -1).status_code == 403
