% pwo_cls_name = pw_object.__class__.__name__
% pw_object_type = pwo_cls_name.lower()
<h1>{{pwo_cls_name}} {{pw_object["name"]}}</h1>
<table>
% for k in pw_object.META["columns"]:
    <tr><td style="text-align:right">{{k}}:</td><td>
%   if k=="init":
    <textarea rows="4" cols="50" name="{{k}}" 'readonly'/>{{pw_object[k]}}</textarea>
%   elif k=="mode":
%       if pwo_cls_name in ("Sensor", "Switch", "Hardware"):
        <select name="mode" 'disabled'>
%       for k in sorted(pw_object.MODE):
            <option value="{{k}}"{{" selected" if pw_object["mode"]==k else ""}}>{{pw_object.MODE[k]}}</option>
%       end
        </select>
%       end
%   else:
    <input type="text" size="60" value="{{pw_object[k]}}" name="{{k}}"  'readonly'/>
%   end
    </td></tr>
% end

<tr><td style="text-align:right">Last Upd Local Time:</td><td>{{pw_upd_local_datetime}}</td></tr>

%if pwo_cls_name == "Hardware":
    % col1, col2 = pw_object.get_html()
<tr><td style="text-align:right">{{col1}}:</td><td>{{!col2}}</td></tr>
%end
</table>
<p><img src="{{image}}" border="1"/></p>

