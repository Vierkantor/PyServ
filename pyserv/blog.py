from datetime import datetime

from .auth import Unspecified, has_auth, levels
from .database import db, DBClass

class BlogPost(DBClass):
	"""A single post with a title, contents and author."""

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Unicode(255))
	contents = db.Column(db.UnicodeText())
	posted = db.Column(db.DateTime(timezone=True))
	last_updated = db.Column(db.DateTime(timezone=True))
	# TEST: when modifying a BlogPost, last_updated >= posted
	"""Can users without blog rights see this post?"""
	public = db.Column(db.Boolean())

	type = db.Column(db.Unicode(255))
	__mapper_args__ = {
			'polymorphic_identity': 'BlogPost',
			'polymorphic_on': type
	}
	def __init__(self, *, title, contents, posted=None, last_updated=None, public=False):
		"""Make a new blog post.
		
		If the time of posting is left None, it will be the time this object is created.
		If the time of last updated is left None, it will be the time it is posted.
		"""
		if posted is None:
			posted = datetime.now()
		if last_updated is None:
			last_updated = posted

		# TEST for last_updated
		assert posted <= last_updated

		self.title = title
		self.contents = contents
		self.posted = posted
		self.last_updated = last_updated
		self.public = public

	def should_see(self, user=Unspecified):
		"""Determine whether the user has enough rights to see this post."""
		return has_auth(levels.blog, user) or self.public

def all_posts(start=0, count=10, user=Unspecified):
	"""Get all blog posts, latest first, from the start number up to some limit.
	
	Note that we define "latest" as the one which has the latest posting timestamp.
	When you want to sort on updates, you might want to extend this function.
	
	Useful for implementing functions like an overview of all posts to the blog.
	"""
	query = BlogPost.query
	# Users with no special rights still have to see the right number of posts
	# so we filter in the database before sending to the client
	if not has_auth(levels.blog, user):
		query = query.filter(BlogPost.public == True)
	return query.order_by(BlogPost.posted.desc()).offset(start).limit(count).all()

