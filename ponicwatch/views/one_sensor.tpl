<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch - Sensor Detail</title>
</head>
<body>
% include('header.html')
<h1>Sensor {{sensor["name"]}}</h1>
<form method="POST" id="form" action="/sensors">
<table>
% for k in ("id","name","mode","init","read_value","calculated_value","timer","updated_on"):
    <tr><td>{{k}}:</td><td><input type="text" value="{{sensor[k]}}" name="{{k}}"  {{ "readonly" if login_logout=="Login" or k=="id" else "" }}/></td></tr>
% end
</table>
% if login_logout=="Logout":
    <input type="submit" value="Update" name="submit" />
%end
</form>
<p><img src="{{image}}" border="1"/></p>
</body>
</html>
