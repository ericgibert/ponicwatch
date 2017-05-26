<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch - {{pw_object.__class__.__name__}} Detail</title>
</head>
<body>
% include('header.html')
<h1>{{pw_object.__class__.__name__}} {{pw_object["name"]}}</h1>
<form method="POST" id="form" action="/{{ pw_object_type }}">
<table>
<!--for k in ("id","name","mode","init","value","timer","timer_interval","updated_on"): -->
% for k in pw_object.META["columns"]:
    <tr><td style="text-align:right">{{k}}:</td><td><input type="text" size="60" value="{{pw_object[k]}}" name="{{k}}" {{ 'readonly' if login_logout=='Login' or k.endswith('_id') else '' }}/></td></tr>
% end
</table>
% if login_logout=="Logout":
    <input type="hidden" value="{{ pw_object['id'] }}" name="id" />
    <input type="hidden" value="{{ pw_object_type }}" name="pw_object_type" />
    <input type="submit" value="Update" name="submit" />
%end
</form>
<p><img src="{{image}}" border="1"/></p>
</body>
</html>
