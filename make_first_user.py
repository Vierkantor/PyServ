#!/usr/bin/env python3
from sys import argv, exit

from pyserv.database import db
from pyserv.person import User
from pyserv.apikey import APIKey

try:
	username = argv[1]
	password = argv[2]
except IndexError:
	print("Usage: ./make_first_user.py <username> <password>")
	exit(1)

first_user = User(full_name="Generic User", nickname=username, password=password)
db.session.add(first_user)
db.session.commit()
print("Created user +{}".format(first_user.id))
