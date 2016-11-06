from os import urandom

from .database import db, DBClass

class APIKey(DBClass):
	"""Allows services to work just like the users.
	
	Prevents that tedious mucking about with sessions and cookies you would need to log in.
	Also makes sure the actual user can revoke them anytime.
	"""
	id = db.Column(db.Integer, primary_key=True)
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	secret_code = db.Column(db.LargeBinary(255), nullable=False)

	def __init__(self, owner):
		self.owner = owner
		self.secret_code = urandom(64)
