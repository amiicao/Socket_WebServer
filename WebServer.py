# Include Python's Socket Library
from socket import *


def normalize_line_endings(s):
    # https://stackoverflow.com/questions/10114224/how-to-properly-send-http-response-with-python-using-socket-library-only
    r'''Convert string containing various line endings like \n, \r or \r\n,
    to uniform \n.'''

    return ''.join((line + '\n') for line in s.splitlines())


# def receive_chunks(sock):
#     has_timed_out = False
#     try:  # timeout will throw error, so we wrap code in a try/catch block
#         socket.settimeout(10)
#         chunks = []
#         ongoing = True
#         while ongoing:
#             data = sock.recv(1024)
#             print("data", data.decode())
#             if not data:
#                 ongoing = False
#                 continue
#             chunks.append(data)
#             print("chunks:", chunks)
#         socket.settimeout(None)
#         total_chunks = ''.join(chunks)
#         print("total_chunks", total_chunks)
#         return total_chunks, has_timed_out
#     except:
#         print("timed out")
#         has_timed_out = True
#     return "", has_timed_out


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

    while True:  # Loop forever
        # Server waits on accept for incoming requests.
        # New socket created on return
        connectionSocket, client_addr = serverSocket.accept()

        # Read from socket (but not address as in UDP)
        data = connectionSocket.recv(1024).decode()
        time_out_flag = False

        # -- STATUS CODE 404 -- check if timeout
        # data, time_out_flag = receive_chunks(connectionSocket) # todo: add 404 feature function
        print("data", data)
        print("timeoutflag", time_out_flag)

        request = normalize_line_endings(data)
        request_head, request_body = request.split('\n\n', 1)

        print("\n----request_head:", request_head)
        print("\n----request_body", request_body)

        # first line is request headline, and others are headers
        request_head = request_head.splitlines()
        request_headline = request_head[0]

        request_headers = dict(x.split(': ', 1) for x in request_head[1:])

        # headline has form of "METHOD URI HTTP/1.0"
        request_method, request_uri, request_proto = request_headline.split(' ', 3)

        print("filename", request_uri)
        # -- STATUS CODE 404 -- check if the page requested exists
        file_not_found = False
        try:
            f = open(request_uri[1:], 'r')
            file_lines = f.readlines()
            response_body = ''.join(file_lines)

        except:
            file_not_found = True
            response_html = ['<html><body><h1>Error 404</h1>', '<p>Not Found</p>', '</body></html>']
            response_body = ''.join(response_html)

        response_headers = {
            'Content-Type': 'text/html; encoding=utf8',
            'Content-Length': len(response_body),
            'Connection': 'close',
        }

        response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                       iter(response_headers.items()))

        # build response status
        response_proto = 'HTTP/1.1'

        if time_out_flag:
            response_status = '408'
            response_status_text = 'Request Timed Out'
        elif file_not_found:
            response_status = '404'
            response_status_text = 'Not Found'
        else:
            response_status = '200'
            response_status_text = 'OK'  # this can be random

        response_status = f'{response_proto} {response_status}  {response_status_text}'
        # sending all this stuff
        connectionSocket.send(response_status.encode())
        connectionSocket.send(response_headers_raw.encode())
        connectionSocket.send('\n'.encode())  # to separate headers from body

        connectionSocket.send(response_body.encode())

        # Close connection to client (but not welcoming socket)
        connectionSocket.close()

run()
