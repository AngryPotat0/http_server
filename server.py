import socket
import os

class httpServer:
    def __init__(self,ip: str, port: int):
        self.file_type = {
            'jpg': 'image/jpeg',
            'png': 'image/png',
            'html': 'text/html'
        }
        self.response_status = ''
        self.response_header = ''
        self.statics = self.loadStatic('static')
        self.soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.soc.bind((ip,port))

    def run(self):
        print("Http Server start running")
        while(True):
            self.soc.listen(5)
            conn,addr = self.soc.accept()
            request = str(conn.recv(1024), encoding = "utf-8")
            print(request)
            request = self.parseRequest(request,addr)
            if(not request):
                print("request error")
                conn.close()
            url_type = request['url'].split('.')[-1]
            if(url_type == 'py'):
                try:
                    py_name = request['url'][1:-3]
                    py_module = __import__(py_name)
                    env = {}
                    response_body = py_module.application(env,self.start_response)
                    response = bytes(self.response_status + os.linesep + self.response_header + os.linesep + response_body, encoding="utf-8")
                    conn.sendall(response)
                    conn.close()
                except ImportError:
                    print("Import error")
                    response = bytes("HTTP/1.1 404 Not Found" + os.linesep, encoding="utf-8")
                    conn.sendall(response)
                    conn.close()
            else:
                try:
                    file_type = ""
                    if(url_type in self.file_type):
                        file_type = self.file_type[url_type]
                    else:
                        file_type = 'text\html'

                    response = bytes('HTTP/1.1 200 OK' + os.linesep + 'Content-Type:%s'% file_type + os.linesep + os.linesep, encoding="utf-8")
                    file = request['url'] if request['url'] != '/' else '/index.html'

                    if(file in self.statics):
                        temp = self.statics[file]
                        if(isinstance(temp,str)):
                            response += bytes(temp,encoding="utf-8")
                        else:
                            response += temp
                    else:
                        response = bytes("HTTP/1.1 404 Not Found" + os.linesep, encoding="utf-8")
                    conn.sendall(response)
                    conn.close()
                except:
                    print("Unknow error")
                    response = bytes("HTTP/1.1 404 Not Found" + os.linesep, encoding="utf-8")
                    conn.sendall(response)
                    conn.close()

    def parseRequest(self,request,addr):
        request_split = request.split('\r\n')
        method, url, version = request_split[0].split(' ')

        requestHead = dict()

        for i in range(1, len(request_split)):
            if (request_split[i] == ''):
                break
            key, value = request_split[i].split(': ')
            requestHead[key] = value

        requestBody = []
        for i in range(2 + len(requestHead), len(request_split)):
            requestBody.append(request_split[i])
        requestBody = '\r\n'.join(requestBody)

        ans = {
            'addr': addr,
            'method': method,
            'url': url,
            'http_version': version,
            'head': requestHead,
            'body': requestBody
        }
        return ans

    def get_file(self, files_dir='.'):
        files_dir = os.path.join(os.getcwd(), files_dir)
        fin = []

        def helper(files_dir='.', path=''):
            if (files_dir[-1:] != '/'):
                files_dir += '/'
            files = os.listdir(files_dir)
            for file in files:
                fpath = os.path.join(files_dir, file)
                if (os.path.isdir(fpath)):
                    helper(fpath, file)
                else:
                    if (path):
                        fin.append('%s/%s' % (path, file))
                    else:
                        fin.append(file)

        helper(files_dir)
        return fin

    def loadStatic(self, static_path='static'):
        files = self.get_file(static_path)
        static_path = os.path.join(os.getcwd(), static_path)
        statics = dict()
        img_file = ('jpg', 'png')
        for file in files:
            suf = file.split('.')[-1]
            file_path = os.path.join(static_path, file)
            if (suf in img_file):
                f = open(file_path, 'rb')
            else:
                f = open(file_path, 'r')
            statics['/' + file] = f.read()
            f.close()
        return statics

    def start_response(self, status, response_headers):
        self.response_status = status
        self.response_header = ''
        for k, v in response_headers:
            kv = k + ':' + v + os.linesep
            self.response_header += kv
