<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch</title>
</head>
<body>
% include('header.html')
<h1>Dashboard for PonicWatch</h1>

<ol>
%for sys in controller.systems.values():
    <li value="{{sys['id']}}">{{sys["name"]}} ({{sys["location"]}})</li>
%end
</ol>

<table border="0">
% for row in rows:
    <tr><td>{{row[2]}}</td><td>{{row[3]}}</td><td>{{row[4]}}</td><td>{{row[5]}}</td><td>{{row[6]}}</td><td>{{row[7]}}</td></tr>
%end
</table>
% from ponicwatch import __version__, __author__, __license__
<p>Version: {{__version__}}<br/>
   Author: &nbsp;{{__author__}}<br/>
   License: {{__license__}}<br/>
</p>

% if session_valid:
Click <a href="/stop">here</a> to stop the application.
% end

</body>
</html>