import base_test

from pyserv.database import db

from test_blog import make_new_post

def test_blog_escapes(client):
	"""HTML tags like <marquee> shouldn't appear in blog titles."""
	post = make_new_post(title="<marquee>Whee!</marquee>")

	response = client.get('/blog')
	base_test.check_response(response)
	assert "<marquee>".encode('utf-8') not in response.data
