from datetime import datetime
from uuid import uuid4

import base_test

from pyserv.database import db
from pyserv.blog import BlogPost, all_posts

from test_login import ensure_logged_in

def make_new_post(commit_change=True):
	"""Make a new blog post with a random title and contents."""
	new_post = BlogPost(title="test{}".format(uuid4()), contents=str(uuid4()), posted=datetime.now())
	if commit_change:
		db.session.add(new_post)
		db.session.commit()
	return new_post

def test_post_limits():
	"""Make a couple of blog posts and check that they appear up to a certain limit."""
	posts_count = 5 # increasing this will quadratically increase number of queries!

	# we optimize the test somewhat by only committing when we're finished
	bogus_posts_1 = list(make_new_post(commit_change=False) for i in range(0, 5))
	expected_posts = list(make_new_post(commit_change=False) for i in range(0, posts_count))
	bogus_posts_2 = list(make_new_post(commit_change=False) for i in range(0, 5))
	db.session.commit()

	for start in range(posts_count, 2 * posts_count):
		for count in range(0, posts_count - start):
			assert all_posts(start=start, count=count) == expected_posts[start:start+count]

def test_post_overview(client):
	"""Make a blog post and ensure it shows up on the front page."""
	post = make_new_post()

	response = client.get('/blog')
	base_test.check_response(response)
	assert post.title.encode('utf-8') in response.data

def test_new_blog(client, blog_user):
	"""Make a blog post via the web interface and ensure it shows up on the front page."""
	# require the right amount of auth - you need to be logged in
	base_test.check_response(client.get('/blog/new'), expected=403)
	# but when you're logged in, you can post
	author = blog_user()
	base_test.check_response(ensure_logged_in(client, author))
	base_test.check_response(client.get('/blog/new'))

	# then post the required data
	title = str(uuid4())
	contents = str(uuid4())
	response = client.post('/blog/new', data={
		"title": title,
		"contents": contents,
	}, follow_redirects=True)
	base_test.check_response(response)
	# and check it appears in the blog posts
	response = client.get('/blog')
	base_test.check_response(response)
	assert title.encode('utf-8') in response.data
	assert contents.encode('utf-8') in response.data
