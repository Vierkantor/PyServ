from pytest import fixture

import pyserv.config
pyserv.config.debug = True
pyserv.config.test = True
pyserv.config.database_uri = 'sqlite:////tmp/test.db'

from pyserv.database import reset_tables
import pyserv.view
from pyserv.app import setup

# set up all the requirements but don't start the server
reset_tables()
setup()

def check_response(response, expected=200):
	"""Check the status code of the response, report the response data if it is invalid."""
	assert response.status_code == expected, response.data.decode('utf-8')
