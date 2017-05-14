<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch</title>
</head>
<body>

% include('header.html')

% for row in rows:
    {{row[0]}} {{row[1]}} <br />
% end

% if current_page > 0:
    <a href="/log/{{current_page-1}}">Previous</a>
% end
% if len(rows) == 20:
    <a href="/log/{{current_page+1}}">Next</a>
% end
</body>
</html>