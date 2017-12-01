<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch - {{pw_object.__class__.__name__}} Detail</title>
</head>
<body>
% include('header.html')
% pwo_cls_name = pw_object.__class__.__name__
% pw_object_type = pwo_cls_name.lower()
<h1>{{pwo_cls_name}} {{pw_object["name"]}}</h1>
<form method="POST" id="form" action="/{{ pw_object_type }}/upd/{{pw_object["id"]}}">
<table>
% for k in pw_object.META["columns"]:
    <tr><td style="text-align:right">{{k}}:</td><td>
%   if k=="init":
    <textarea rows="4" cols="50" name="{{k}}" {{ 'readonly' if login_logout=='Login' else '' }}/>{{pw_object[k]}}</textarea>
%   else:
    <input type="text" size="60" value="{{pw_object[k]}}" name="{{k}}" {{ '' if login_logout=='Logout' and k in ("name","timer") else 'readonly' }}/>
%   end
    </td></tr>
% end

<tr><td style="text-align:right">Last Upd Local Time:</td><td>{{pw_upd_local_datetime}}
        <a href="/log?system={{pwo_cls_name.upper()}}_{{pw_object["id"]}}">Go to Log page</a></td></tr>

%if pwo_cls_name == "Hardware":
    % col1, col2 = pw_object.get_html()
<tr><td style="text-align:right">{{col1}}:</td><td>{{!col2}}</td></tr>
%end

%if pwo_cls_name == "Sensor":
<tr><td style="text-align:right"> </td>
    <td><button onclick="location.href='/sensor/read/{{pw_object["id"]}}'" type="button">Execute reading...</button></td></tr>
%end

%if pwo_cls_name == "Interrupt":
<tr><td style="text-align:right"> </td>
    <td><button onclick="location.href='/interrupt/exec/{{pw_object["id"]}}'" type="button">Execute interruption callback...</button></td></tr>
%end

%if pwo_cls_name == "Switch":
<tr><td style="text-align:right"> </td>
    <td><button onclick="location.href='/switch/exec/{{pw_object["id"]}}'" type="button">Set switch to {{pw_object.init_dict["set_value_to"]}} ...</button></td></tr>
%end

</table>

    <input type="hidden" value="{{ pw_object['id'] }}" name="id" />
    <input type="hidden" value="{{ pw_object_type }}" name="pw_object_type" />
% if login_logout=="Logout":
    <input type="submit" value="Update" name="submit" />
%end
</form>
<p><img src="{{image}}" border="1"/></p>
</body>
</html>
