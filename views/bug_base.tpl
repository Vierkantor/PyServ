<%!
 from pyserv.bug import BugPriority, BugStatus
%>

<%def name="show_enum(member)">
 <%
 try:
  value = member.value
 except AttributeError:
  value = str(member)
 %>
 ${value}
</%def>

<%def name="table_head()">
 <tr>
  <th>Number</th>
  <th>Status</th>
  <th>Priority</th>
  <th>Title</th>
 </tr>
</%def>

<%def name="table_row(bug)">
 <tr>
  <td>${bug.id}</td>
  <td>${show_enum(bug.status)}</td>
  <td>${show_enum(bug.priority)}</td>
  <td>${bug.title}</td>
 </tr>
</%def>

<%def name="current_status(bug)">
 <p>
  <strong>Status:</strong> ${show_enum(bug.status)}<br>
  <strong>Priority:</strong> ${show_enum(bug.priority)}<br>
 </p>
</%def>

<%def name="messages(bug)">
 <% prev_title = prev_status = prev_priority = None %>
 % for message in bug.messages:
  ${list_message(message, prev_title, prev_status, prev_priority)}
  <hr>
  <%
  if message.new_title is not None: prev_title = message.new_title
  if message.new_status is not None: prev_status = message.new_status
  if message.new_priority is not None: prev_priority = message.new_priority
  %>
 % endfor
</%def>

<%def name="list_message(bug_message, prev_title=None, prev_status=None, prev_priority=None)">
 <ul>
  % if bug_message.new_title is not None:
   <li><strong>Title:</strong> ${prev_title} ↦ ${bug_message.new_title}</li>
  % endif
  % if bug_message.new_status is not None:
   <li><strong>Status:</strong> ${show_enum(prev_status)} ↦ ${show_enum(bug_message.new_status)}</li>
  % endif
  % if bug_message.new_priority is not None:
   <li><strong>Priority:</strong> ${show_enum(prev_priority)} ↦ ${show_enum(bug_message.new_priority)}</li>
  % endif
 </ul>
 ${bug_message.description}
</%def>

<%def name="status_input(name='status', selected=None)">
 <select id="${name}" name="${name}">
  % for status in BugStatus:
   <option value="${status.name}" ${"selected" if status==selected else ""}>
    ${show_enum(status)}
   </option>
  % endfor
 </select>
</%def>

<%def name="priority_input(name='priority', selected=None)">
 <select id="${name}" name="${name}">
  % for priority in BugPriority:
   <option value="${priority.name}" ${"selected" if priority==selected else ""}>
    ${show_enum(priority)}
   </option>
  % endfor
 </select>
</%def>
