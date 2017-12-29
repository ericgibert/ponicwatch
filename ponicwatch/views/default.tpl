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

%import os
<p>Database file size: {{os.path.getsize(controller.db.server_params["database"]) >> 10}} kB</p>
% from ponicwatch import __version__, __author__, __license__
<p>Version: {{__version__}}<br/>
   Author: &nbsp;{{__author__}}<br/>
   License: {{__license__}}<br/>
</p>
<ul>
% import sys
    <li>Python: {{sys.version}}</li>
% import sqlite3
    <li>sqlite3: {{sqlite3.version}}</li>
% import bottle
    <li>bottle: {{bottle.__version__}}</li>
% import apscheduler
    <li>apscheduler: {{apscheduler.__version__}}</li>
% import markdown
    <li>markdown: {{markdown.version}}</li>
% import matplotlib
    <li>matplotlib: {{matplotlib.__version__}}</li>
</ul>
<table border="1">
% for row in rows:
    <tr><td>{{row[0]}}</td><td>{{row[2]}}</td><td>{{row[3]}}</td><td>{{row[4]}}</td><td>{{row[5]}}</td><td>{{row[6]}}</td><td>{{row[7]}}</td></tr>
%end
</table>

<p>
% if session_valid:
Click <a href="/stop">here</a> to stop the application.
% end
</p>
</body>
</html>