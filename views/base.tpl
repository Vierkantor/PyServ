<!DOCTYPE html>
<html lang="${lang}">
 <head>
  ## note that the cow has a lot of spaces on the end of the line because we had to get rid of backslashes on the end of a line and html end-of-comment syntax
  <!--
 __________________________________  
/ There are no easter eggs on this \ 
| website, I promise!              | 
\__________________________________/ 
        \   ^__^                     
         \  (oo)\_______             
            (__)\       )\/\         
                ||-__-w |            
                ||     ||            
  -->
  <title>${self.title()}</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  <meta name="description" content="A web server written in Python, and some related programmings."/>
  ## include the basic stylesheet and any others we might need (passed in by the controller)
  ${stylesheet('base')}
  % if stylesheets:
   % for sheet in stylesheets:
    ${stylesheet(sheet)}
   % endfor
  % endif
 </head>
 <body>
  <%include file="navbar.tpl"/>
  ## contains all other divs - handy for creating a bit of padding on either side
  <div class="all">
   <div class="header">
    <%block name="body_header">
     <h1><%block name="title">PyServ</%block></h1>
    </%block>
   </div>
   <% messages = get_flashed_messages() %>
   % if messages:
    <div class="messages">
     % for message in messages:
      <div class="message">${message}</div>
     % endfor
    </div>
   % endif
   <div class="body">
    ${next.body()}
   </div>
   <div class="footer">
    <%block name="body_footer">
     <ul class="footnotes">
      <li>Created by Vierkantor. You can get their e-mail address by placing that name on both sides of an '@' sign and adding '.com' on the end.</li>
      <li>PyServ is free software. You can get some PyServ for yourself!</li>
     </ul>
    </%block>
   </div>
  </div>
 </body>
</html>

<%def name="stylesheet(sheet_name)">
 <link rel="stylesheet" href="${url_for('static', filename='style/'+sheet_name+'.css')}" type="text/css"/>
</%def>
