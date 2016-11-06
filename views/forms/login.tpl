<form action="${url_for('login_form', next=request.path)}" method="POST">
	<input type="text" name="user"/>
	<input type="password" name="pass"/>
	<input type="submit" name="submit" value="Log in"/>
</form>
