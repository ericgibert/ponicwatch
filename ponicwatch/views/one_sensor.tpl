<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch - Sensor Detail</title>
</head>
<body>
% include('header.html')
<h1>Sensor {{sensor["name"]}}</h1>
<table>
% for k in ("id","name","mode","init","read_value","calculated_value","timer","updated_on"):
    <tr><td>{{k}}:</td><td>{{sensor[k]}}</td></tr>
% end
</table>
</body>
</html>