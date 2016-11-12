from datetime import datetime

from .database import db, DBClass

class BlogPost(DBClass):
	"""A single post with a title, contents and author."""

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Unicode(255))
	contents = db.Column(db.UnicodeText())
	posted = db.Column(db.DateTime(timezone=True))
	last_updated = db.Column(db.DateTime(timezone=True))
	# TEST: when modifying a BlogPost, last_updated >= posted

	type = db.Column(db.Unicode(255))
	__mapper_args__ = {
			'polymorphic_identity': 'BlogPost',
			'polymorphic_on': type
	}
	def __init__(self, *, title, contents, posted=None, last_updated=None):
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

def all_posts(start=0, count=10):
	"""Get all blog posts, latest first, from the start number up to some limit.
	
	Note that we define "latest" as the one which has the latest posting timestamp.
	When you want to sort on updates, you might want to extend this function.
	
	Useful for implementing functions like an overview of all posts to the blog.
	"""
	return BlogPost.query.order_by(BlogPost.posted.desc()).offset(start).limit(count).all()
