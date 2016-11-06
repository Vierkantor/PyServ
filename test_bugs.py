from flask import session
from random import choice
from uuid import uuid4

import base_test

from pyserv.bug import Bug, BugPriority, BugStatus, BugUserMessage, new_message
from pyserv.database import db

def test_empty_bug_overview(client):
	"""Viewing the bug overview with no bugs shouldn't produce an error."""
	response = client.get('/service/bug')
	base_test.check_response(response)
	assert b'No bugs' in response.data

def make_new_bug():
	"""Make a new bug with no messages in it and a random title."""
	new_bug = Bug(title="test{}".format(uuid4()))
	db.session.add(new_bug)
	db.session.commit()
	return new_bug

def test_new_bug_overview(client):
	"""After making a bug, we should see it in the overview."""
	new_bug = make_new_bug()

	response = client.get('/service/bug')
	base_test.check_response(response)
	assert new_bug.title.encode('utf-8') in response.data

def test_view_nonexistent_bug_page(client):
	"""When the bug id is wrong, we should get an error page."""

	response = client.get('/service/bug/-1')
	base_test.check_response(response, 404)

def test_view_bug_page(client):
	"""When we have made a bug, check that its page exists."""
	new_bug = make_new_bug()

	response = client.get('/service/bug/{}'.format(new_bug.id))
	base_test.check_response(response)
	assert new_bug.title.encode('utf-8') in response.data

def test_new_bug(client):
	"""Make a new bug via the form and verify we get the correct page."""
	title = str(uuid4())
	priority = choice(list(BugPriority))
	status = choice(list(BugStatus))
	description = str(uuid4())

	response = client.post('/service/bug/new',
			data={
				"title": title,
				"priority": priority.name,
				"status": status.name,
				"description": description,
			},
			follow_redirects=True,
	)
	base_test.check_response(response)
	assert title.encode('utf-8') in response.data
	assert priority.value.encode('utf-8') in response.data
	assert status.value.encode('utf-8') in response.data
	assert description.encode('utf-8') in response.data

def test_bug_reaction(client):
	"""Make a new bug and try to send messages.
	
	The first one has some random fields, while the other ones modify only one.
	"""
	bug = make_new_bug()

	# change out all the fields
	title = str(uuid4())
	priorities = list(BugPriority)
	priorities.remove(bug.priority)
	priority = choice(priorities)
	statuses = list(BugStatus)
	statuses.remove(bug.status)
	status = choice(statuses)
	description = str(uuid4())
	message = new_message(BugUserMessage,
			bug, description, title=title, status=status, priority=priority
	)
	assert message.new_title == title
	assert message.new_priority == priority
	assert message.new_status == status

	# change out the title
	title = str(uuid4())
	message = new_message(BugUserMessage,
			bug, description, title=title, status=status, priority=priority
	)
	assert message.new_title == title
	assert message.new_priority is None
	assert message.new_status is None

	# change out the priority
	priorities.remove(priority)
	priority = choice(priorities)
	message = new_message(BugUserMessage,
			bug, description, title=title, status=status, priority=priority
	)
	assert message.new_title is None
	assert message.new_priority == priority
	assert message.new_status is None

	# change out the status
	statuses.remove(status)
	status = choice(statuses)
	message = new_message(BugUserMessage,
			bug, description, title=title, status=status, priority=priority
	)
	assert message.new_title is None
	assert message.new_priority is None
	assert message.new_status == status
