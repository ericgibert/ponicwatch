<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch</title>
</head>
<body>
% include('header.html')
%if error:
<p><fieldset><legend>Notice</legend>{{error}}</fieldset></p>
%end

<form method="POST" id="form" action="/Login">
    <table>
        <tr><td>Login name: </td><td> <input type="text" name="username" /></td></tr>
        <tr><td>Password: </td><td> <input type="password" name="password" /></td></tr>
    </table>
    <input type="submit" value="Login" name="submit" />
</form>
</body>
</html>
