import os  # provides functs for interacting with the os since we are checking if file exists
import socket #provides connection between client viz browser here and server
class HTTPServer:#The actual HTTP server class.

    headers = {
        'Server': "Shubhi's server",#name of the server 
        'Content-Type': 'text/html',#type of content 
    }

    status_codes = { #status codes 
        200: 'OK',
        404: 'Not Found',
        301: 'Moved Permanently',
    }


    def __init__(self, host='127.0.0.1', port=4040):#address of server and port of server
        self.host = host
        self.port = port
        self.method = None
        self.uri = None
        self.http_version = '1.1' # default to HTTP/1.1 


    def start(self): #Method for starting the server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#create socket object with IP address and network type
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#SO_REUSEADDR option should be set for all sockets being bound  to the port you want to bind multiple socket onto, not only for new socket.
        s.bind((self.host, self.port))#binds the socket object to the address and port
        s.listen(5)# start listening for connections here atmost 5 connections
        print("Listening at", s.getsockname())
        while True:
            c, addr = s.accept()#accept client requests
            print("Connected by", addr) 
            data = c.recv(1024) #reading just the first 1024 bytes sent by the client.
            response= self.handle_request(data)#handle_request method which will then returns a response
            c.sendall(response)# send back the data to client
            c.close()# close the connection

    
    def handle_request(self, data):#handles requests
        lines = data.split(b'\r\n')#here we parse the request line to get the method , uri and http version
        request_line = lines[0] # request line is the first line of the data
        words = request_line.split(b' ') # split request line into seperate words
        self.method = words[0].decode() # call decode to convert bytes to string
        if len(words) > 1:
            self.uri = words[1].decode() # call decode to convert bytes to string
        if len(words) > 2:
            self.http_version = words[2].decode()
        response = self.handle_GET() #assume that its always a get request
        return response


    def handle_GET(self):#handle get request
        path = self.uri.strip('/') # remove slash from URI
        if not path:
            path = 'index.html'
        if path=="moveto.html":
            response_line = self.response_line(301)
            response_headers = self.response_headers({
                "Location" : "https://www.google.co.in/"
            })
            response_body =b''
        elif os.path.exists(path) and not os.path.isdir(path): # don't serve directories
            response_line = self.response_line(200)
            response_headers = self.response_headers()
            with open(path, 'rb') as f: #read the requested html files
                response_body = f.read()
        else:
            response_line = self.response_line(404) #if requested file is not found
            response_headers = self.response_headers()
            response_body = b'<h1>404 Not Found</h1>'
        blank_line = b'\r\n'
        response = b''.join([response_line, response_headers, blank_line, response_body])#joins all the components together
        return response
    

    def response_line(self, status_code):# returns response line based on status code
        reason = self.status_codes[status_code]#key status returns corresponding values as reason
        response_line = 'HTTP/1.1 %s %s\r\n' % (status_code, reason)#HTTP/1.1 200 OK
        return response_line.encode() # convert from str to bytes

    def response_headers(self, extra_headers=None):#Returns headers (as bytes).
        headers_copy = self.headers.copy() # make a local copy of headers

        if extra_headers:
            headers_copy.update(extra_headers)

        headers = ''

        for h in headers_copy:
            headers += '%s: %s\r\n' % (h, headers_copy[h])#server:shubhi's server

        return headers.encode() # convert str to bytes


if __name__ == '__main__':
    server = HTTPServer()
    server.start()
