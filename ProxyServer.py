# Include Python's Socket Library
import time
from socket import *

# Specify Proxy Server Address
ProxyServerHost = '127.0.0.1' # todo: replace with my computer's ip address after
ProxyServerPort = 12000

# Specify Main Server Address
MainServerHost = '127.0.0.1'  # todo: replace with my computer's ip address after
MainServerPort = 80

response_status_text = {
    '200': 'OK',
    '304': 'Not Modified',
    '400': 'Bad request',
    '404': 'Not Found',
    '408': 'Request Timed Out'
}

def normalize_line_endings(s):
    # https://stackoverflow.com/questions/10114224/how-to-properly-send-http-response-with-python-using-socket-library-only
    r'''Convert string containing various line endings like \n, \r or \r\n,
    to uniform \n.'''

    return ''.join((line + '\n') for line in s.splitlines())


def fetch_file(filename):
    print("client requested filename", filename)

    try:
        # look for unsafe characters, status code 400
        if "{" in filename or "}" in filename or "[" in filename or "]" in filename or "%" in filename or "|" in filename or "^" in filename or "`" in filename or "~" in filename or "//" in filename:
            status_code = '400'
            response_html = ['<html><body><h1>Error 400</h1>', '<p>Bad Request</p>', '</body></html>']
            response_body = ''.join(response_html)
            return response_body, status_code

        cache_f = open(f'proxy_cache/{filename}', 'r')
        cache_file_lines = cache_f.readlines()
        cache_f.close()
        print("----------opened proxy folder")

        server_f = open(f'server_files/{filename}', 'r')
        server_file_lines = server_f.readlines()
        server_f.close()
        print("----------opened server folder")

        # compare cache file with server file; if different, status code 304; else status code 200
        if cache_file_lines != server_file_lines:
            print("cached file is different from server file!")
            status_code = '404'  # todo: hack to enable something to show on webpage; 304 doesn't work
            response_html = ['<html><body><h1>Error 304</h1>', '<p>Not Modified</p>', '</body></html>']
            response_body = ''.join(response_html)
            return response_body, status_code

        else:
            print("cached file is same as server file!")
            status_code = '200'
            response_body = ''.join(cache_file_lines)
            return response_body, status_code

    except:  # file is not in cache, need to fetch it from server
        if fetch_file_from_server(filename):
            cache_f = open(f'proxy_files/{filename}', 'r')
            cache_file_lines = cache_f.readlines()
            cache_f.close()

            status_code = '200'
            response_body = ''.join(cache_file_lines)
            return response_body, status_code

        else:
            print(f'server does not have {filename}!!')
            status_code = '404'
            response_html = ['<html><body><h1>Error 404</h1>', '<p>Not Found</p>', '</body></html>']
            response_body = ''.join(response_html)
            return response_body, status_code


def fetch_file_from_server(filename):
    print(f"trying to fetch {filename} from main server")
    # create TCP socket and connect to Main Server Socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((MainServerHost,MainServerPort))

    # send name of file to request from Main Server
    clientSocket.send(f'GET /proxy-request-{filename} HTTP/1.1\n\n'.encode())
    try:
        with open(f'proxy_cache/{filename}', "wb") as f:
            while True:
                bytes_read = clientSocket.recv(1024)
                if not bytes_read:
                    break
                f.write(bytes_read)
                clientSocket.close()
        return True
    except:
        clientSocket.close()
        return False



def run():
    # Create TCP Socket for Proxy Server
    ProxySocket = socket(AF_INET, SOCK_STREAM, proto=0)

    # Bind the proxy server port to the socket
    ProxySocket.bind((ProxyServerHost, ProxyServerPort))

    # Server begins listening for incoming TCP connections
    backlog = 10  # max number of queued connections
    ProxySocket.listen(backlog)

    print('The server is ready to receive')

    while True:  # Loop forever
        # Server waits on accept for incoming requests.
        # New socket created on return
        connectionSocket, client_addr = ProxySocket.accept()

        # implement a timer
        start_time = time.time()
        # sleep function used to artificially create the request timeout
        # time.sleep(7)
        time_recv = time.time() - start_time
        if (time_recv < 5):

            # Read from socket (but not address as in UDP)
            data = connectionSocket.recv(1024).decode()

            print("\n----data", data, "\n------------------------------\n")

            request = normalize_line_endings(data)
            request_head, request_body = request.split('\n\n', 1)

            print("\n----request_head:", request_head, "\n------------------------------\n")
            # print("\n----request_body", request_body, "\n------------------------------\n")

            # first line is request headline, and others are headers
            request_head = request_head.splitlines()
            request_headline = request_head[0]

            # headline has form of "GET URI HTTP/1.0"
            request_method, request_uri, request_proto = request_headline.split(' ', 3)

            print("filename", request_uri)

            response_body, response_status = fetch_file(request_uri[1:])

            # build response status
            response_status_line = f'HTTP/1.1 {response_status} {response_status_text[response_status]}'

            # build response headers
            response_headers = {
                'Content-Type': 'text/html; encoding=utf8',
                'Content-Length': len(response_body),
                'Connection': 'close',
            }
            response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                           iter(response_headers.items()))

            # sending full response
            connectionSocket.send(response_status_line.encode())
            connectionSocket.send(response_headers_raw.encode())
            connectionSocket.send('\n'.encode())  # to separate headers from body
            connectionSocket.send(response_body.encode())

            # Close connection to client (but not welcoming socket)
            connectionSocket.close()

        else:  # timeout; status code 408
            response_status = '408'
            response_html = ['<html><body><h1>Error 408</h1>', '<p>Request Timeout</p>', '</body></html>']
            response_body = ''.join(response_html)

            # build response status
            response_status_line = f'HTTP/1.1 {response_status} {response_status_text[response_status]}'

            # build response headers
            response_headers = {
                'Content-Type': 'text/html; encoding=utf8',
                'Content-Length': len(response_body),
                'Connection': 'close',
            }
            response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                           iter(response_headers.items()))

            # sending full response
            connectionSocket.send(response_status_line.encode())
            connectionSocket.send(response_headers_raw.encode())
            connectionSocket.send('\n'.encode())  # to separate headers from body
            connectionSocket.send(response_body.encode())

        print(response_body)
        # Close connection to client (but not welcoming socket)
        connectionSocket.close()


run()
