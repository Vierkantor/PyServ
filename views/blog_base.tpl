<%def name="title(post)">
%if post.public:
 ${post.title}
%else:
 ${post.title} (Private)
%endif
</%def>
<%def name="sneak_peek(post)">
 <div class="sneak_peek">
  <h2>${title(post)}</h2>
  <p class="post_contents">${post.contents}</p>
 </div>
</%def>
