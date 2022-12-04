# Include Python's Socket Library
from socket import *


def normalize_line_endings(s):
     # https://stackoverflow.com/questions/10114224/how-to-properly-send-http-response-with-python-using-socket-library-only
    r'''Convert string containing various line endings like \n, \r or \r\n,
    to uniform \n.'''

    return ''.join((line + '\n') for line in s.splitlines())


def run():
     serverPort = 80  # HTTP services are usually on port 80
     # http://127.0.0.1:80/test.html copy and paste this into the browser to send request to server
     serverHost = '127.0.0.1'  # todo: replace with my computer's ip address after

     # Create TCP welcoming socket
     serverSocket = socket(AF_INET, SOCK_STREAM, proto=0)

     # Bind the server port to the socket
     serverSocket.bind((serverHost, serverPort))

     # Server begins listening for incoming TCP connections
     backlog = 10  # max number of queued connections
     serverSocket.listen(backlog)

     print('The server is ready to receive')


     while True: # Loop forever
          # Server waits on accept for incoming requests.
          # New socket created on return
          connectionSocket, client_addr = serverSocket.accept()

          # Read from socket (but not address as in UDP)
          data = connectionSocket.recv(1024).decode()

          request = normalize_line_endings(data)
          request_head, request_body = request.split('\n\n', 1)

          print("\n----request_head:", request_head)
          print("\n----request_body", request_body)

          # first line is request headline, and others are headers
          request_head = request_head.splitlines()
          request_headline = request_head[0]
          # headers have their name up to first ': '. In real world uses, they
          # could duplicate, and dict drops duplicates by default, so
          # be aware of this.
          request_headers = dict(x.split(': ', 1) for x in request_head[1:])

          # headline has form of "METHOD URI HTTP/1.0"
          request_method, request_uri, request_proto = request_headline.split(' ', 3)


          f = open(request_uri[1:], 'r')
          file_lines = f.readlines()

          response_body = ''.join(file_lines)

          response_headers = {
               'Content-Type': 'text/html; encoding=utf8',
               'Content-Length': len(response_body),
               'Connection': 'close',
          }

          response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                         iter(response_headers.items()))

          # Reply as HTTP/1.1 server, saying "HTTP OK" (code 200).
          response_proto = 'HTTP/1.1'
          response_status = '200'
          response_status_text = 'OK'  # this can be random

          response_status = f'{response_proto} {response_status}  {response_status_text}'
          # sending all this stuff
          connectionSocket.send(response_status.encode())
          connectionSocket.send(response_headers_raw.encode())
          connectionSocket.send('\n'.encode())  # to separate headers from body


          connectionSocket.send(response_body.encode())


          # Close connectiion too client (but not welcoming socket)
          connectionSocket.close()

run()