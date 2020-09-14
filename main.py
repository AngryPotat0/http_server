import socket
import os

def parseRequest(request,addr):

    request_split = request.split('\r\n')
    print(request_split[0])
    method, url,version = request_split[0].split(' ')

    requestHead = dict()

    for i in range(1,len(request_split)):
        if(request_split[i] == ''):
            break
        key,value = request_split[i].split(': ')
        requestHead[key] = value

    requestBody = []
    for i in range(2 + len(requestHead),len(request_split)):
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

def get_file(files_dir = '.'):
    files_dir = os.path.join(os.getcwd(),files_dir)
    fin = []
    def helper(files_dir = '.', path = ''):
        if(files_dir[-1:] != '/'):
            files_dir += '/'
        files = os.listdir(files_dir)
        for file in files:
            fpath = os.path.join(files_dir,file)
            if(os.path.isdir(fpath)):
                helper(fpath,file)
            else:
                if(path):
                    fin.append('%s/%s' % (path,file))
                else:
                    fin.append(file)
    helper(files_dir)
    return fin

def loadStatic(static_path = 'static'):
    files = get_file(static_path)
    static_path = os.path.join(os.getcwd(),static_path)
    statics = dict()
    img_file = ('jpg','png')
    for file in files:
        suf = file.split('.')[-1]
        file_path = os.path.join(static_path,file)
        if(suf in img_file):
            f = open(file_path,'rb')
        else:
            f = open(file_path,'r')
        statics['/' + file] = f.read()
        f.close()
    return statics

def main():
    statics = loadStatic('static')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 8080))
    while (True):
        s.listen(5)
        conn, addr = s.accept()
        request = str(conn.recv(1024),encoding = "utf-8")
        print(request)
        if not request:
            conn.close()
        request = parseRequest(request,addr)
        file_type = {
            'jpg': 'image/jpeg',
            'png': 'image/png',
            'html': 'text/html'
        }
        suf = request['url'].split('.')[-1]
        tyep = ""
        if(suf in file_type):
            type = file_type[suf]
        else:
            type = 'text/html'
        response = bytes('HTTP/1.1 200 OK\r\nContent-Type:%s\r\n\r\n' % type,encoding = "utf-8")

        if(request['url'] in statics):
            temp = statics[request['url']]
            if(isinstance(temp,str)):
                response += bytes(statics[request['url']], encoding="utf-8")
            else:
                response += statics[request['url']]


        conn.sendall(response)
        conn.close()

main()
