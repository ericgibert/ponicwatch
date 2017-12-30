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
%   elif k=="mode":
%       if pwo_cls_name in ("Sensor", "Switch", "Hardware"):
        <select name="mode" {{ 'disabled' if login_logout=='Login' else '' }}>
%       for k in sorted(pw_object.MODE):
            <option value="{{k}}"{{" selected" if pw_object["mode"]==k else ""}}>{{pw_object.MODE[k]}}</option>
%       end
        </select>
%       end
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
    <td><button type="button" onclick="location.href='/sensor/exec/{{pw_object["id"]}}'">Execute reading...</button></td></tr>
%end

%if pwo_cls_name == "Interrupt":
<tr><td style="text-align:right"> </td>
    <td><button type="button" onclick="location.href='/interrupt/exec/{{pw_object["id"]}}'">Execute interruption callback...</button></td></tr>
%end

%if pwo_cls_name == "Switch":
<tr><td style="text-align:right"> </td>
    <td><button type="button" onclick="location.href='/switch/exec/{{pw_object["id"]}}'">Set switch to {{pw_object.init_dict["set_value_to"]}} ...</button></td></tr>
%end
<tr><td>
    <input type="hidden" value="{{ pw_object['id'] }}" name="id" />
    <input type="hidden" value="{{ pw_object_type }}" name="pw_object_type" />
% if login_logout=="Logout":
    <input type="submit" value="Update" name="submit" />
%end
</td><td><button type="button" onclick="get_value('{{pw_object_type}}', {{pw_object["id"]}})">Check value</button>
    <div id="value_text"></div>
</td>
</tr>
</table>
</form>
<p><img src="{{image}}" border="1"/></p>
<script type="text/javascript" language="javascript">
function get_value(pwo_cls, id)
{
    var xhttp = new XMLHttpRequest();
    var url = "/" + pwo_cls + "/value/" + id;
    xhttp.open("GET", url, true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            var response = JSON.parse(this.responseText);
            var msg = "<p>this.value = " + response["value"] + "</p><hr/>"
                    + "<p>['if']: " + response["if"] + "</p><p>make: " + response["make"]
                    + "</p><p>eval = " + response["eval"] + "</p>";
            document.getElementById('value_text').innerHTML = msg;
        }
    }
    xhttp.send();
}
</script>
</body>
</html>
