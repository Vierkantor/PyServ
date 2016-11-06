<%namespace name="bug_view" file="../bug_base.tpl"/>

<form action="${url_for('bug_message', bug_id=bug.id)}" method="POST">
	<label for="title">Title</label> <input type="text" id="title" name="title" size="30" value="${bug.title}"/><br/>
	<label for="status">Status</label> ${bug_view.status_input(selected=bug.status)}<br/>
	<label for="priority">Priority</label> ${bug_view.priority_input(selected=bug.priority)}<br/>
	<label for="description">Description:</label><br/>
	<textarea id="description" name="description"></textarea><br/>
	<input type="submit" name="submit" value="Report!"/>
</form>

