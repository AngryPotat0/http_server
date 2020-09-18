from server import httpServer

ip = 'localhost'
port = 8080
s = httpServer(ip,port)
s.run()