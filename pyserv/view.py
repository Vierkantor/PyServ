"""Provide the view for the basic site.

Most basic pages are defined here, but any subsites have their own views.
You could technically consider them more of a controller, but the whole MVC thing is overplayed.
"""

from datetime import datetime
from flask import abort, flash, redirect, request, session, url_for
import flask_mako

from .apikey import APIKey
from .app import app
from .auth import has_auth, levels, require_auth, set_shadow_user
from .bug import Bug, BugPriority, BugStatus, BugUserMessage, bug_from_user, get_all_bugs, new_message
from .blog import BlogPost, all_posts
from . import config
from .database import db
from .person import User, get_login, get_logged_in

@app.context_processor
def inject_lang():
	"""Pages automatically report their language as English."""
	return {'lang': 'en'}
@app.context_processor
def inject_auth():
	"""You can access various auth functions from templates."""
	return {
			'has_auth': has_auth,
			'levels': levels,
	}
@app.context_processor
def inject_current_user():
	"""Grant access to the logged in user (and the shadowed user)."""
	app.logger.debug(session)
	if 'shadow_user' in session:
		assert session['current_user'] is not None
		assert config.debug # in case of any accidents
		return {'current_user': get_logged_in(), 'shadow_user_id': session['shadow_user']}
	else:
		return {'current_user': get_logged_in()}

def render_template(*args, **kwargs):
	"""A wrapper for flask_mako.render_template that also renders the Mako template error."""
	try:
		return flask_mako.render_template(*args, **kwargs)
	except flask_mako.TemplateError as e:
		return e.text, 500

@app.route('/')
def front_page():
	return render_template('front_page.html')

@app.route('/service/api_key', methods=["GET", "POST"])
@require_auth(levels.logged_in)
@require_auth(levels.no_key)
def api_key_overview():
	return render_template('api_key_overview.html')

@app.route('/service/api_key/create', methods=["GET", "POST"])
@require_auth(levels.logged_in)
@require_auth(levels.no_key)
def create_api_key():
	if request.method == "POST":
		user = get_logged_in()
		key = APIKey(user)
		db.session.add(key)
		db.session.commit()
		flash('Created key "{}".'.format(key))
		return redirect(url_for('api_key_overview'))
	else:
		return render_template('create_api_key_form.html')

@app.route('/service/shadow_user', methods=["GET", "POST"])
@require_auth(levels.shadow_god)
def shadow_user_form():
	if request.method == "POST":
		assert config.debug # prevent accidents
		current_user = request.form.get('user_id', '')
		try:
			current_user = int(current_user)
		except ValueError:
			current_user = None
		set_shadow_user(current_user)
		if 'shadow_user' in session:
			flash('shadowing +{}'.format(session['current_user']))
		else:
			flash('not shadowing')
		return render_template('shadow_user_form.html')
	else:
		if not config.debug:
			return render_template('shadow_user_production.html')
		else:
			return render_template('shadow_user_form.html')

@app.route('/service/login', methods=["GET", "POST"])
def login_form():
	if request.method == "POST":
		user = request.form.get('user', '')
		password = request.form.get('pass', '')
		next_page = request.args.get('next', '')
		# check username and password
		current_user = get_login(user, password)
		if current_user is None:
			app.logger.info("authentication attempt failed")
			flash("Invalid credentials.")
			return render_template('login_form.html')
		session['current_user'] = current_user.id
		# display the page
		flash("You were logged in.")
		if not next_page or next_page == url_for('login_form'):
			return render_template('login_okay.html')
		return redirect(next_page)
	else:
		return render_template('login_form.html')
@app.route('/service/logout')
def logout():
	next_page = request.args.get('next', '')
	session.pop('current_user', None)
	session.pop('shadow_user', None)
	flash('You were logged out.')
	if not next_page:
		return redirect('/')
	return redirect(next_page)

@app.route('/user/<user_id>')
def user_profile(user_id):
	user = User.query.get(user_id)
	if user is None:
		abort(403)
	return render_template('user_profile.html', user=user)

@app.route('/service/bug')
def bug_overview():
	return render_template('bug_overview.html', bugs=get_all_bugs())

@app.route('/service/bug/new', methods=["GET", "POST"])
def bug_report():
	if request.method == "POST":
		title = request.form.get('title', 'Untitled bug')
		status = request.form.get('status', BugStatus.default().name)
		priority = request.form.get('priority', BugPriority.default().name)
		description = request.form.get('description', '')

		status = BugStatus[status]
		priority = BugPriority[priority]

		new_bug = bug_from_user(title=title, status=status, priority=priority, description=description)

		db.session.add(new_bug)
		db.session.commit()
		flash('Created bug #{}'.format(new_bug.id))

		return redirect(url_for('bug_profile', bug_id=new_bug.id))
	else:
		return render_template('bug_form.html')

@app.route('/service/bug/<bug_id>')
def bug_profile(bug_id):
	bug = Bug.query.get_or_404(bug_id)
	return render_template('bug_profile.html', bug=bug)

@app.route('/service/bug/<bug_id>/message', methods=["POST"])
def bug_message(bug_id):
	bug = Bug.query.get_or_404(bug_id)

	title = request.form.get('title', bug.title)
	status = request.form.get('status', bug.status.name)
	priority = request.form.get('priority', bug.priority.name)
	description = request.form.get('description', '')

	status = BugStatus[status]
	priority = BugPriority[priority]

	message = new_message(BugUserMessage,
			bug, description, title=title, status=status, priority=priority
	)

	db.session.add(bug)
	db.session.commit()

	flash("Message posted!")
	return redirect(url_for('bug_profile', bug_id=bug.id))

@app.route('/service/bug/search/api', methods=["POST"])
def bug_search_api():
	term = request.form.get("term", "")
	if not term:
		return {}
	from_title = Bug.query.filter(Bug.title.like(term)).all()
	return from_title

@app.route('/blog')
def blog_overview():
	return render_template("blog_overview.html", posts=all_posts(start=0, count=10))
@app.route('/blog/new', methods=["GET", "POST"])
@require_auth(levels.blog)
def blog_new_post():
	if request.method == "GET":
		return render_template("blog_new_post.html")
	title = request.form.get('title', 'A Blog Post to Never Forget')
	contents = request.form.get('contents', '')
	public = bool(request.form.getlist('public'))
	new_post = BlogPost(title=title, contents=contents, posted=datetime.now(), public=public)
	db.session.add(new_post)
	db.session.commit()
	flash("Post blogged!")
	return redirect(url_for('blog_post_profile', post_id=new_post.id))

@app.route('/blog/<post_id>')
def blog_post_profile(post_id):
	post = BlogPost.query.get(post_id)
	if not post or not (post.public or has_auth(levels.blog)):
		# return 403 to not leak any information about public posts
		return abort(403)
	return render_template('post_profile.html', post=post)

@app.route('/blog/<post_id>/edit', methods=["GET", "POST"])
@require_auth(levels.blog)
def blog_edit_post(post_id):
	post = BlogPost.query.get(post_id)
	if not post or not (post.public or has_auth(levels.blog)):
		# return 403 to not leak any information about public posts
		return abort(403)
	if request.method == "GET":
		return render_template('blog_edit_post.html', post=post)

	# TODO: genericize this whole construction for new/edit
	# TODO: genericize this whole construction for other objects
	post.title = request.form.get('title', post.title)
	post.contents = request.form.get('contents', post.contents)
	post.public = bool(request.form.getlist('public'))
	post.last_updated = datetime.now()
	db.session.add(post)
	db.session.commit()
	flash("Your post has been updated!")
	return redirect(url_for('blog_post_profile', post_id=post.id))
