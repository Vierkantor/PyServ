<div id="navbar">
 <ul class="navbar-items-left">
  <li><a href="${url_for('front_page')}">Home</a></li>
 </ul>
 <ul class="navbar-items-right">
  <li>
   ## login check
   % if current_user:
    <a href="${url_for('user_profile', user_id=current_user.id)}">
     ${current_user.personal_name}
    </a>
   % else:
    <%include file="forms/login.tpl"/>
   % endif
  </li>
 </ul>
</div>
