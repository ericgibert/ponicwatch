<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch</title>
</head>
<body>
% include('header.html')
<h3>All links</h3>

<table border="1">
    <tr><th>Active</th><th>System</th><th>Sensor</th><th>Switch</th><th>Hardware</th><th>Interrupt</th><th>Creation Order</th></tr>
% for row in controller.links:
<tr><td style="text-align:center">{{ "X" if row[0]>0 else "-" }}</td>
    <td>{{ controller.get_pwo("system",abs(row[0])) }}</td>
    <td>{{ (controller.get_pwo("sensor",row[1]) or 'id: %s' % row[1]) if row[1] else "-" }}</td>
    <td>{{ (controller.get_pwo("switch",row[2]) or 'id: %s' % row[2]) if row[2] else "-"  }}</td>
    <td>{{ (controller.get_pwo("hardware",row[3]) or 'id: %s' % row[3]) if row[3] else "-"  }}</td>
    <td>{{ (controller.get_pwo("interrupt",row[5]) or 'id: %s' % row[5]) if row[5] else "-"  }}</td>
    <td>{{row[4]}}</td>
% end
</table>
</body>
</html>