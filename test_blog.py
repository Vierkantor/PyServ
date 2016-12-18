from datetime import datetime
from uuid import uuid4

import base_test

from pyserv.database import db
from pyserv.blog import BlogPost, all_posts

from test_login import ensure_logged_in

def make_new_post(commit_change=True, title=None, contents=None, public=True):
	"""Make a new blog post with a random title and contents.
	If title or contents are given, use those values instead.
	"""
	if title is None:
		title = "test{}".format(uuid4())
	if contents is None:
		contents = str(uuid4())
	new_post = BlogPost(title=title, contents=contents, public=public)

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

def test_visibility(client, blog_user):
	"""Check that private posts are invisible to regular users but not to blog users."""
	post_private = make_new_post(public=False)
	post_public = make_new_post(public=True)
	posts_no_auth = all_posts(start=0, count=2, user=None)
	assert post_private not in posts_no_auth
	assert not post_private.should_see(None)
	assert post_public in posts_no_auth
	assert post_public.should_see(None)

	author = blog_user()
	posts_auth = all_posts(start=0, count=2, user=author)
	assert post_private in posts_auth
	assert post_private.should_see(author)
	assert post_public in posts_auth
	assert post_public.should_see(author)

def test_private_accessibility(client):
	"""Check that private posts can't be seen through url manipulation."""
	post_private = make_new_post(public=False)
	response = client.get('/blog/{}'.format(post_private.id))
	base_test.check_response(response, expected=403)

def test_edit_blog(client, blog_user):
	"""Make a blog post via the web interface and ensure it shows up on the front page."""
	post = make_new_post()
	edit_url = '/blog/{}/edit'.format(post.id)

	# require the right amount of auth - you need to be logged in
	base_test.check_response(client.get(edit_url), expected=403)
	# but when you're logged in, you can post
	author = blog_user()
	ensure_logged_in(client, author)
	base_test.check_response(client.get(edit_url))

	# then post the required data
	title = str(uuid4())
	contents = str(uuid4())
	response = client.post(edit_url, data={
		"title": title,
		"contents": contents,
	}, follow_redirects=True)
	base_test.check_response(response)
	# and check it appears in the blog posts
	response = client.get('/blog')
	base_test.check_response(response)
	assert title.encode('utf-8') in response.data
	assert contents.encode('utf-8') in response.data

def test_editing_updates_values(client, blog_user):
	"""When editing a blog post, the last updated time should be automatically
	changed to be right when the update was sent out."""

	# give us the right amount of auth
	author = blog_user()
	ensure_logged_in(client, author)

	# make a post that is very old
	post = make_new_post(commit_change=False)
	post.last_updated = datetime.fromtimestamp(0)
	db.session.add(post)
	db.session.commit()

	before_update = datetime.now()

	# update it a bit
	edit_url = '/blog/{}/edit'.format(post.id)
	base_test.check_response(client.post(edit_url, data={
		"contents": str(uuid4()),
	}, follow_redirects=True))

	# and check that it has changed
	updated_post = BlogPost.query.get(post.id)
	assert updated_post.last_updated >= before_update
