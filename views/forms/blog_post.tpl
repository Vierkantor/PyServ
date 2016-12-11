<%namespace name="blog_view" file="../blog_base.tpl"/>

<%
if post:
	action = url_for('blog_edit_post', post_id=post.id)
	title = post.title
	contents = post.contents
	public = int(post.public)
else:
	action = url_for('blog_new_post')
	title = ""
	contents = ""
	public = 0
%>
<form action="${action}" method="POST">
	<label for="title">Title</label> <input type="text" id="title" name="title" value="${title}" size="30"/><br/>
	<label for="contents">Description:</label><br/>
	<textarea id="contents" name="contents">${contents}</textarea><br/>
	<label for="public">Public</label> <input type="checkbox" id="public" name="public" ${"checked" if public else ""}/><br/>
	<input type="submit" name="submit" value="Publish!"/>
</form>

