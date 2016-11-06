from enum import Enum

from .database import db, DBClass

class BugStatus(Enum):
	# open: when you can work on it
	New = "New"
	Confirmed = "Confirmed"
	InProgress = "In progress"
	Testing = "Being tested"
	# closed: when you can work on it
	TestPassed = "Test passed"
	Deployed = "Deployed"

	# open: when you can't work on it
	FeedbackRequired = "Feedback required"
	# closed: when you can't work on it
	NotABug = "Not a bug"
	Duplicate = "Duplicate"
	Closed = "Closed"
	Postponed = "Postponed"

	@classmethod
	def default(cls):
		return cls.New

open_statuses = {
		BugStatus.New,
		BugStatus.Confirmed,
		BugStatus.InProgress,
		BugStatus.Testing,
		BugStatus.FeedbackRequired,
}
closed_statuses = {
		BugStatus.TestPassed,
		BugStatus.Deployed,
		BugStatus.NotABug,
		BugStatus.Duplicate,
		BugStatus.Closed,
		BugStatus.Postponed,
}

class BugPriority(Enum):
	Insignificant = "Insignificant"
	Low = "Low"
	Medium = "Medium"
	High = "High"
	Urgent = "Urgent"

	@classmethod
	def default(cls):
		return cls.Insignificant

class Bug(DBClass):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Unicode(255))
	# CHECK this is the same as in BugMessage
	status = db.Column(db.Enum(BugStatus))
	priority = db.Column(db.Enum(BugPriority))
	messages = db.relationship('BugMessage', backref='bug', lazy='dynamic')

	type = db.Column(db.Unicode(255))
	__mapper_args__ = {
			'polymorphic_identity': 'Bug',
			'polymorphic_on': type
	}

	def __init__(self, *,
			title,
			status=BugStatus.New, priority=BugPriority.Insignificant):
		self.title = title
		self.status = status
		self.priority = priority

class BugMessage(DBClass):
	"""A single message that updates the values of the bug."""

	id = db.Column(db.Integer, primary_key=True)
	bug_id = db.Column(db.Integer, db.ForeignKey('bug.id'))
	# CHECK this is the same as Bug
	new_title = db.Column(db.Unicode(255))
	new_status = db.Column(db.Enum(BugStatus))
	new_priority = db.Column(db.Enum(BugPriority))

	type = db.Column(db.Unicode(255))
	__mapper_args__ = {
			'polymorphic_identity': 'BugMessage',
			'polymorphic_on': type
	}

	def __init__(self, bug, *,
			title=None, status=None, priority=None):
		"""Constructor for the BugMessage class.
		
		Does not modify any field in the parent Bug.
		For that, use the new_message function.
		(Or directly call self.update().)
		"""
		self.bug = bug
		self.new_title = title
		self.new_status = status
		self.new_priority = priority

	@property
	def description(self):
		"""The human-readable motivation for the message.
		
		Should be overrided in the child classes.
		"""
		return ""

	def update(self):
		"""Set the parent Bug's fields to the values in this Message."""
		if self.new_title is not None:
			self.bug.title = self.new_title
		if self.new_priority is not None:
			self.bug.priority = self.new_priority
		if self.new_status is not None:
			self.bug.status = self.new_status

class BugUserMessage(BugMessage):
	"""A message manually entered by a user."""
	id = db.Column(db.Integer, db.ForeignKey('bug_message.id'), primary_key=True)

	__mapper_args__ = {
			'polymorphic_identity': 'BugUserMessage',
	}

	description = db.Column(db.Unicode(255))

	def __init__(self, bug, description, **kwargs):
		super().__init__(bug, **kwargs)
		self.description = description

def bug_from_user(*, title, status, priority, description):
	"""Make a new Bug from a user's report.
	
	This will not save the bug in the database!
	"""
	new_bug = Bug(title=title, status=status, priority=priority)
	new_message = BugUserMessage(new_bug, description, title=title, status=status, priority=priority)

	return new_bug

def get_all_bugs(statuses=open_statuses):
	"""Get all bugs with one of the given statuses."""

	# TODO: is this really the best way to do this?
	result = []
	for status in statuses:
		result.extend(Bug.query.filter_by(status=status).all())
	return result

def new_message(message_cls, bug, *args, title=None, status=None, priority=None, **kwargs):
	"""Create a new BugMessage that is the last update to the Bug.
	
	Will set the Bug's fields to this message's fields, if applicable.
	"""
	# don't modify things when they're already the same
	if title == bug.title:
		title = None
	if status == bug.status:
		status = None
	if priority == bug.priority:
		priority = None
	message = message_cls(bug, *args, title=title, status=status, priority=priority, **kwargs)
	message.update()
	return message
