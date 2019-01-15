<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch</title>
</head>
<body>
% include('header.html')
<h1>Dashboard</h1>

<ol>
%for sys in controller.systems.values():
    <li value="{{sys['id']}}">{{sys["name"]}} ({{sys["location"]}})</li>
%end
</ol>


% from ponicwatch import __version__, __author__, __license__
<p><h3>Ponicwatch:</h3>
   - Version: {{__version__}}<br/>
% from http_view import __version__
   - http_view: {{__version__}}<br/>
   - Author: &nbsp;{{__author__}}<br/>
   - License: {{__license__}}<br/>
</p>
%import os
<p>Database file size: {{os.path.getsize(controller.db.server_params["database"]) >> 10}} kB</p>
<ul>
    <li>Last stop on:  {{controller.last_stop[0]}}</li>
    <li>Last start on: {{controller.last_start[0]}}</li>
</ul>
<table border="1">
% for row in rows:
    <tr><td>{{row[0]}}</td><td>{{row[2]}}</td><td>{{row[3]}}</td><td>{{row[4]}}</td><td>{{row[5]}}</td><td>{{row[6]}}</td><td>{{row[7]}}</td></tr>
%end
</table>

<p>
% if session_valid:
<hr/>
<ul>
    % import sys
    <li>Python: {{sys.version}}</li>
    % import sqlite3
    <li>sqlite3: {{sqlite3.version}}</li>
    % import pkg_resources
    <li>bottle: {{ pkg_resources.get_distribution("bottle").version}}</li>
    <li>APScheduler: {{pkg_resources.get_distribution("apscheduler").version}}</li>
    <li>Markdown: {{pkg_resources.get_distribution("markdown").version}}</li>
    <li>matplotlib: {{pkg_resources.get_distribution("matplotlib").version}}</li>
    % try:
    <li>pigpio: {{pkg_resources.get_distribution("pigpio").version}}</li>
    % except pkg_resources.DistributionNotFound:
    <li>pigpio: not installed</li>
    <li>tzlocal: {{pkg_resources.get_distribution("tzlocal").version}}</li>
</ul>
<b><a href="/restart">Restart</a></b> the application.
<hr/>
To stop the application, click <a href="/stop">here</a>.
% end
</p>
</body>
</html>