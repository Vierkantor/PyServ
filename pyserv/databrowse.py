from sys import exit

# TODO: generate configuration automatically if it's missing
from . import config
from . import app
from .database import prepare_tables
from . import view # load all the views

def main():
	# setup
	prepare_tables()
	# run!
	app.run()
