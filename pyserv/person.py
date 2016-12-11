from flask import session
from hashlib import pbkdf2_hmac
from os import urandom

from .database import db, DBClass

class Contact(DBClass):
	id = db.Column(db.Integer, primary_key=True)
	full_name = db.Column(db.Unicode(255))

	type = db.Column(db.Unicode(255))
	__mapper_args__ = {
			'polymorphic_identity': 'Contact',
			'polymorphic_on': type
	}

	def __init__(self, *, full_name):
		self.full_name = full_name

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			raise NotImplemented()
		if self.id is None or other.id is None:
			raise NotImplemented()
		return self.id == other.id

class Person(Contact):
	id = db.Column(db.Integer, db.ForeignKey('contact.id'), primary_key=True)
	personal_name = db.Column(db.Unicode(255))
	nickname = db.Column(db.Unicode(255), unique=True, nullable=False)

	__mapper_args__ = {
			'polymorphic_identity': 'Person',
	}

	def __init__(self, *, nickname, personal_name = None, **kwargs):
		super().__init__(**kwargs)
		if not personal_name:
			personal_name = self.full_name
		self.personal_name = personal_name
		self.nickname = nickname

class User(Person):
	id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)
	"""The user's password, in a hashed form.
	
	The non-hashed format should !!NEVER!! be stored permanently,
	because that is a giant, hideous security breach.
	"""
	password = db.Column(db.LargeBinary(255), nullable=False)
	"""Salt for hashing the password."""
	salt = db.Column(db.LargeBinary(255), nullable=False)

	# see also apikey.py
	api_keys = db.relationship('APIKey', backref='owner', lazy='dynamic')

	__mapper_args__ = {
			'polymorphic_identity': 'User',
	}

	def __init__(self, *, password, **kwargs):
		super().__init__(**kwargs)
		self.salt = urandom(64)
		self.password_from_unhashed(password)

	def password_from_unhashed(self, unhashed):
		"""Set the user's password from an unhashed string."""
		self.password = pbkdf2_hmac('sha256', unhashed.encode('utf-8'), self.salt, 100000)

	def __repr__(self):
		return "User <{} '{}'>".format(self.id, self.full_name)

def get_login(name, password):
	"""Get the user with given name or password, or None if not found."""
	user = User.query.filter_by(nickname=name).first()
	if user is None:
		return None
	pass_hash = pbkdf2_hmac('sha256', password.encode('utf-8'), user.salt, 100000)
	if pass_hash != user.password:
		return None
	return user

def get_logged_in():
	"""Get the user that is currently logged in, or None otherwise."""
	if 'current_user' in session:
		return User.query.get(session['current_user'])
