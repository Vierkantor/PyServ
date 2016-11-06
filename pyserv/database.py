from flask_sqlalchemy import SQLAlchemy

from .app import app

db = SQLAlchemy(app)
DBClass = db.Model

def prepare_tables():
	db.create_all()

def reset_tables():
	"""Get rid of all data in the database.

	This will irrevocably deliberately destroy every little piece of data forever
	(and that is a very long time!)
	so running it in production is disabled.
	"""
	from . import config
	if not config.debug:
		raise ValueError("you can't truncate tables in production!")
	db.drop_all()
	db.create_all()
