import BaseHTTPServer
server_address = ('127.0.0.1', 31337)
handler_class = BaseHTTPServer.BaseHTTPRequestHandler
httpd = BaseHTTPServer.HTTPServer(server_address, handler_class)
httpd.serve_forever()