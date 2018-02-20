<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch - {{pw_object.__class__.__name__}}  List</title>
</head>
<body>
% include('header.html')
<p>
% if pw_object:
    <table border="1">
        <tr>
    % for k in pw_object.META["columns"]:
            <th>{{ k }}</th>
    % end
        </tr>
    % for row in rows:
        % if row[0] in ctrl_pwo_dict:
    <tr><td><a href="/{{ pw_object_type }}/{{row[0]}}">{{row[0]}}</a></td>
        <td><a href="/{{ pw_object_type }}/{{row[0]}}">{{row[1]}}</a></td>
        % else:
        <tr><td>{{row[0]}}</td>
            <td>{{row[1]}}</td>
        % end
    % for k in range(2, len(pw_object.META["columns"])):
        <td>{{row[k]}}</td>
    % end
    </tr>
    % end
    </table>
% else:
    <h3>Empty list - no such object defined on this system</h3>
% end
</p>
</body>
</html>