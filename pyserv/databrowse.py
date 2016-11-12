from sys import exit

try:
	from . import config
except ImportError:
	print("""Cannot start: no configuration file found!
	See pyserv/config.py.example for an example file.""")
	exit(1)
from . import app
from .database import prepare_tables
from . import view # load all the views

def main():
	# setup
	prepare_tables()
	# run!
	app.run()
