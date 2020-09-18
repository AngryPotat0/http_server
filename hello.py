def application(env,start_response):
    status = 'HTTP/1.1 200 OK'
    response_headers = [('Server', 'bfe/1.0.8.18'), ('Date', '%s' % time.ctime()), ('Content-Type', 'text/plain')]
    start_response(status, response_headers)

    response_body = "Hello World"
    return response_body