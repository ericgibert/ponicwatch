<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch</title>
</head>
<body>
% include('header.html')
<table border="1">
    <tr><th>log_id</th><th>Controller</th><th>System</th><th>value</th><th>time stamp</th></tr>
% for row in rows:
<tr><td>{{row[0]}}</td>
    <td>{{row[1]}}</td>
    <td><a href="/log?system={{int(row[2])*1000+int(row[3])}}">{{row[4]}}</a></td>
    <td>{{row[5]}}</td>
    <td>{{row[7]}}</td></tr>
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