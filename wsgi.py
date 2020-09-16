from wsgiref.simple_server import make_server

def main():
    server = make_server('localhost',8001,hello)
    print("HTTP on")
    server.serve_forever()

def hello(environ, start_response):
    status = "200 OK"
    response_head = [('Content-Type','text/html')]
    start_response(status,response_head)
    path = environ['PATH_INFO'][1:] or 'hello'
    return [b'<h1> %s </h1>' % path.encode()]

main()