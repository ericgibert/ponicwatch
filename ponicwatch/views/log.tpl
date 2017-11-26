<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch</title>
</head>
<body>
% include('header.html')
% import datetime
<p>{{!pwo}}</p>
<table border="1">
    <tr><th>log_id</th><th>Log Type</th><th>System/PWO</th><th>Value</th><th>Text</th><th>Timestamp</th></tr>
% for row in rows:
<tr><td>{{row[0]}}</td>
    <td>{{row[2]}}</td>
    <td><a href="/log?system={{row[2]+'_'+str(row[3])}}">{{row[4]}}</a></td>
    <td>{{row[5]}}</td>
    <td>{{row[6] if row[2] in ("INFO", "WARNING", "ERROR") else ""}}</td>
    <td>{{row[7].replace(tzinfo=datetime.timezone.utc).astimezone()}}</td></tr>
% end
</table>
<p>
% if current_page > 0:
    <a href="/log/{{current_page-1}}">Previous</a>
% end
% if len(rows) == 20:
    <a href="/log/{{current_page+1}}">Next</a>
% end
</p>
</body>
</html>