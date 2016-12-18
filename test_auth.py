import base_test

from pyserv.auth import has_auth, levels

def test_any_auth(client, test_user):
	"""Sanity check: any user has the auth level `any`."""

	# without logging in, we should have this auth
	assert has_auth(levels.any, None)

	# and with logging in, we should have this auth
	assert has_auth(levels.any, test_user())

def test_god_auth(client, god_user):
	"""A god user should have all auth levels."""
	user = god_user()
	for level in levels:
		assert has_auth(level, user)
