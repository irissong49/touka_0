<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset = "UTF-8">
    <title>Touka prototype0</title>
</head>
<body>
    <h1> Talk to Touka </h1>
    <table>
        {% for l in line %}
            <tr>
                <td> {{l}} </td>
            </tr>
        {% endfor%}
    </table>
    <form method = "post">
        <div>
            <input type ="text" name= "text" placeholder="type here">
        </div>
    </form>
</body>
</html>