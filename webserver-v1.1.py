#
#  webserver.py
#  Simple HTTP Web Server
#
#  Created by mpuchkov on 2019-11-08.
#

from socket import *
from datetime import datetime
import sys
import time
import errno

# Status codes
OK       = (200, 'OK')
NotFound = (404, 'Not Found')

# Convert a (code, phrase) tuple to an HTTP response string
#   Ex:     (404, 'Not Found')   ->   'HTTP/1.1 404 Not Found'
def http_response(status_code, version = '1.1'):
    (number, phrase) = status_code
    header = 'HTTP/{version} {codeNumber} {codePhrase}\r\n'
    return header.format(version = version,
                      codeNumber = str(number),
                      codePhrase = phrase)

# Display sent or received HTTP messages and their length, source,
#   destination, and time.
def log(message, title = 'New HTTP Message', from_addr = '', to_addr = ''):
    print('> {}: '.format(title))
    print('  - Content: {} '.format(message))
    print('  - Length:  {} bytes'.format( str(len(message)) ))
    print('  - From:    {}'.format(from_addr))
    print('  - To:      {}'.format(to_addr))
    print('  - Time:    {} UTC'.format( datetime.utcnow() ))




# Create a TCP server socket, assign a port number,
# bind to server socket and listen for new connections
serverSocket = socket(AF_INET, SOCK_STREAM)
serverHost = 'localhost'
serverPort = 6789
serverAddr = (serverHost, serverPort)

#MARK: 	1. PREPARE SERVER SOCKET
# Bind server's socket to address "http://localhost:6789".
# Begin waiting (listening) for new clients to connect.
serverSocket.bind(serverAddr)
serverSocket.listen(1)


while True:
	print('\nThe server is ready to serve...')

#   #MARK: 	2. ACCEPT CONNECTIONS FROM CLIENTS
	(connectionSocket, clientAddr) = serverSocket.accept()
	print('Server is connected to client {}'.format(clientAddr))
	
	try:
		# Receive and log the GET request message from the client
		request = connectionSocket.recv(1024)
		log(request, 'Received new request from client', clientAddr, serverAddr)
        
		# The path is the second part of HTTP header, identified by [1]
		filename = request.decode().split()[1]
        # Because the extracted path of the HTTP request includes
        #   a character '\', we read the path from the second character
		f = open(filename[1:])
        # Store the entire contenet of the requested file in a temporary
		outputdata = f.read()
		
#       #MARK: 	3. RESPOND WITH '200 OK'
		# If file is found on the server, respond with '200 OK'
		response = http_response(OK).encode()
		connectionSocket.send(response)
		log(response, 'Sending response to client', serverAddr, clientAddr)
 
        # Send the content of the requested file to the client
		for i in range(0, len(outputdata)):
			connectionSocket.send(outputdata[i].encode())
		connectionSocket.send('\r\n'.encode())
		
		# Close the client connection socket
		connectionSocket.close()
		
	except IOError as e:
		# Do not use a client's broken socket to .send()
		#   to disconnected terminals
		if e.errno != errno.EPIPE:
        
#           #MARK: 	4. RESPOND WITH '404 Not Found'
			# If the file is not on the server, respond with '404 Not Found'
			response = http_response(NotFound).encode()
			connectionSocket.send(response)
			log(response, 'Sending response to client', serverAddr, clientAddr)
			
			# Close the client connection socket
			connectionSocket.close()


serverSocket.close()
sys.exit()
