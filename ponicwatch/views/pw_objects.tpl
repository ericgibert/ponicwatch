<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch - {{pw_object.__class__.__name__}}  List</title>
</head>
<body>
% include('header.html')
<table border="1">
    <tr>
% for k in pw_object.META["columns"]:
        <th>{{ k }}</th>
% end
    </tr>
% for row in rows:
<tr><td><a href="/{{ pw_object_type }}/{{row[0]}}">{{row[0]}}</a></td>
    <td><a href="/{{ pw_object_type }}/{{row[0]}}">{{row[1]}}</a></td>
% for k in range(2, len(pw_object.META["columns"])):
    <td>{{row[k]}}</td>
% end
</tr>
% end
</table>
</body>
</html>