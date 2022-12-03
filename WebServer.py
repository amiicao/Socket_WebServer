# Include Python's Socket Library
from socket import *

serverPort = 80   # HTTP services are usually on port 80
# http://127.0.0.1:80/test.html copy and paste this into the browser to send request to server
serverHost = '127.0.0.1' # todo: replace with my computer's ip address after

# Create TCP welcoming socket
serverSocket = socket(AF_INET, SOCK_STREAM, proto=0)

# Bind the server port to the socket
serverSocket.bind((serverHost, serverPort))

# Server begins listening for incoming TCP connections
backlog = 10  # max number of queued connections
serverSocket.listen(backlog)

print ('The server is ready to receive')

while True: # Loop forever
     # Server waits on accept for incoming requests.
     # New socket created on return
     connectionSocket, client_addr = serverSocket.accept()
     
     # Read from socket (but not address as in UDP)
     data = connectionSocket.recv(1024).decode()
     
     # Send the reply

     response = data # todo: make the reply by having the data be formatted with http protocol
     connectionSocket.send(response.encode())
     
     # Close connectiion too client (but not welcoming socket)
     connectionSocket.close()
