<%def name="title(post)">
%if post.public:
 ${post.title}
%else:
 ${post.title} (Private)
%endif
</%def>
<%def name="sneak_peek(post)">
 <div class="sneak_peek">
  <h2><a href="${url_for('blog_post_profile', post_id=post.id)}">${title(post)}</a></h2>
  <p class="post_contents">${post.contents}</p>
 </div>
</%def>
<%def name="post_buttons(post)">
 <div class="post_buttons">
  <a href="${url_for('blog_edit_post', post_id=post.id)}" class="button">Edit</a>
 </div>
</%def>
