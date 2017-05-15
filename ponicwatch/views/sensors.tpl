<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch - Sensor List</title>
</head>
<body>
% include('header.html')
<table border="1">
    <tr><th>sensor_id</th><th>Name</th><th>Mode</th><th>Timer</th><th>Read Val</th><th>Calc Val</th><th>time stamp</th></tr>
% for row in rows:
<tr><td><a href="/sensors/{{row[0]}}">{{row[0]}}</a></td>
    <td>{{row[1]}}</td>
    <td>{{row[2]}}</td>
    <td>{{row[4]}}</td>
    <td>{{row[5]}}</td>
    <td>{{row[6]}}</td>
    <td>{{row[8]}}</td></tr>
% end
</table>
</body>
</html>