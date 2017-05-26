<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch - Switch List</title>
</head>
<body>
% include('header.html')
<table border="1">
    <tr><th>switch_id</th><th>Name</th><th>Mode</th><th>Timer</th><th>Value</th><th>time stamp</th></tr>
% for row in rows:
<tr><td><a href="/switches/{{row[0]}}">{{row[0]}}</a></td>
    <td><a href="/switches/{{row[0]}}">{{row[1]}}</a></td>
    <td>{{row[2]}}</td>
    <td>{{row[4]}}</td>
    <td>{{row[5]}}</td>
    <td>{{row[7]}}</td></tr>
% end
</table>
</body>
</html>