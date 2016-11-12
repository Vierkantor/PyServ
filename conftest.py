import pytest

def pytest_runtest_makereport(item, call):
	if "incremental" in item.keywords:
		if call.excinfo is not None:
			parent = item.parent
			parent._previousfailed = item

def pytest_runtest_setup(item):
	if "incremental" in item.keywords:
		previousfailed = getattr(item.parent, "_previousfailed", None)
		if previousfailed is not None:
			pytest.xfail("previous test failed (%s)" %previousfailed.name)

@pytest.fixture
def client():
	"""Make requests using this client.
	
	Invokes the context manager so you can immediately access values like `flask.session.
	"""
	from pyserv.app import app
	client = app.test_client()
	with client:
		yield client

@pytest.fixture
def test_user():
	"""A factory for users with unique nickname and no other special powers."""
	import uuid
	from pyserv.database import db
	from pyserv.person import User
	def make_test_user():
		password = ""
		test_user = User(full_name="Test User", nickname="test{}".format(uuid.uuid4()), password=password)
		# allow the user to actually log in
		test_user._actual_password = password
		db.session.add(test_user)
		db.session.commit()
		return test_user
	return make_test_user
@pytest.fixture
def god_user(test_user):
	"""A factory for users with unique nickname and god level powers."""
	from pyserv import config
	from pyserv.database import db
	def make_god_user():
		god_user = test_user()
		god_user.full_name="God User"
		db.session.add(god_user)
		db.session.commit()
		config.god_ids.add(god_user.id)
		return god_user
	return make_god_user
@pytest.fixture
def blog_user(test_user):
	"""A factory for users that may write blog articles."""
	return god_user(test_user) # TODO: when we've implemented actual blog auth, be less subtle
