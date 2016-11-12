<%namespace name="blog_view" file="../blog_base.tpl"/>

<form action="${url_for('blog_new_post')}" method="POST">
	<label for="title">Title</label> <input type="text" id="title" name="title" size="30"/><br/>
	<label for="contents">Description:</label><br/>
	<textarea id="contents" name="contents"></textarea><br/>
	<label for="public">Public</label> <input type="checkbox" id="public" name="public"/><br/>
	<input type="submit" name="submit" value="Publish!"/>
</form>

