<!DOCTYPE html>
<html lang="${request.locale_name}">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="pyramid web application">
    <meta name="author" content="Pylons Project">
    <link rel="shortcut icon" href="${request.static_url('dirshare:static/pyramid-16x16.png')}">
    <title>DirImageStream</title>
    <link href="${request.static_url('dirshare:static/theme.css')}" rel="stylesheet">
    <script src="${request.static_url('dirshare:static/jquery.min.js')}" type="text/javascript"></script>
  </head>

  <body>
    ${self.body()}
  </body>
</html>
