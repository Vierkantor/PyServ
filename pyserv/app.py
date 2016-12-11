import flask

from . import config

app = flask.Flask("databrowse")
app.config['SQLALCHEMY_DATABASE_URI'] = config.database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MAKO_DEFAULT_FILTERS'] = ['h']

"""Remember whether our app has already run through setting up everything.."""
_is_setup = False

def setup(**kwargs):
	from flask_mako import MakoTemplates

	app.template_folder = "views"
	app.secret_key=config.secret_key
	app.config.update(kwargs)
	mako = MakoTemplates(app)

	_is_setup = True

def run(**kwargs):
	if not _is_setup:
		setup(**kwargs)
	app.run(host=config.host, port=config.port, debug=config.debug)
