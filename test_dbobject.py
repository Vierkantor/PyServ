from pyserv.person import User

import base_test
from pyserv.database import db
def test_user_equality():
	"""A user loaded from the database should test equal to the original one."""
	original_user = User(full_name="Test User", nickname="test_user_equality", password="")
	db.session.add(original_user)
	db.session.commit()
	loaded_user = User.query.filter_by(nickname='test_user_equality').first()
	assert original_user == loaded_user
