from enum import Enum
from flask import abort, session
from functools import wraps

from .app import app
from . import config
from .person import User, get_logged_in

class levels(Enum):
	"""The possible authorization levels.
	
	See has_auth and require_auth for using these.
	When adding another auth level, add an entry to _auth_lookup.
	"""
	any = 0
	logged_in = 1
	god = 2 # access to everything
	shadow_god = 3 # the user or the shadow_user is a god
	no_key = 4 # the user is not using an API key
	blog = 5 # the user may make new blog posts and edit their own

def _has_auth_any(user):
	return True
def _has_auth_logged_in(user):
	return user is not None
def _has_auth_god(user):
	return user is not None and user.id in config.god_ids
def _has_auth_shadow_god(user):
	# Note that this condition shouldn't be true,
	# as long as the has_auth function doesn't change.
	# Of course, that's a bit of a dangerous assumption.
	if _has_auth_god(user):
		return True
	if 'shadow_user' in session:
		return session['shadow_user'] in config.god_ids
def _has_auth_no_key(user):
	if 'current_user' not in session:
		return False
	return user.id == session['current_user']
def _has_auth_blog(user):
	return False # TODO let non-gods make blog posts

_auth_lookup = {
	levels.any: _has_auth_any,
	levels.logged_in: _has_auth_logged_in,
	levels.god: _has_auth_god,
	levels.shadow_god: _has_auth_shadow_god,
	levels.no_key: _has_auth_no_key,
	levels.blog: _has_auth_blog,
}

Unspecified = object()
def has_auth(level, user=Unspecified):
	"""Does the user have the given authorization level?

	Not passing an argument means the currently logged in user (if any),
	passing in None means a user that isn't logged in.
	This is basically a giant ball of special-casing, which you can find elsewhere in this file.
	"""
	if user is Unspecified:
		user = get_logged_in()
	if _has_auth_god(user):
		return True
	return _auth_lookup[level](user)
def require_auth(level):
	"""Decorator for requiring an auth level in a route function."""
	def require_auth_decorator(func):
		@wraps(func)
		def wrapped(*args, **kwargs):
			if not has_auth(level):
				return abort(403)
			return func(*args, **kwargs)
		return wrapped
	return require_auth_decorator

def set_shadow_user(current_user):
	"""Impersonate the given user, or if None, stop impersonating.
	
	This requires you to be on the debug website.
	"""
	assert config.debug
	if current_user is None or User.query.get(current_user) is None:
		if 'shadow_user' not in session:
			app.logger.debug("can't unshadow - already unshadowed")
			return
		# get rid of shadowing
		app.logger.debug("ending shadowing for {}".format(session['shadow_user']))
		session['current_user'] = session.pop('shadow_user', None)
		return

	# don't overwrite the shadow user
	if 'shadow_user' not in session:
		session['shadow_user'] = session['current_user']
	session['current_user'] = current_user
	app.logger.debug("{} is shadowing {}".format(session['shadow_user'], session['current_user']))
