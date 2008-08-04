## @package network
#  Socket operations for client/server communications.

import asyncore, asynchat, socket, sys, string
import world, command, archive, libsigma
from common import *

## Encapsulates a client socket.
class client_socket(asynchat.async_chat):
	## Construct a client socket using an incoming connection.
	#  @arg connection The incoming connection.
	def __init__(self, connection):
		asynchat.async_chat.__init__(self, connection)
		
		## Holds all pending text (awaiting a newline from client).
		self.buffer = ''
		
		self.set_terminator('\n')
		
		## Retains the player class tied to this socket.
		self.parent = world.player(self)

	## Add input data to the buffer and handle backspaces.
	#  @arg data The data from the socket.
	def collect_incoming_data(self, data):
		for char in data:
			if char == '\b' and len(self.buffer) > 0:
				self.buffer = self.buffer[:-1]
			elif char == '\b' or char == '\r': pass
			elif char in string.printable:
				self.buffer += char

	## Overriden member function called when the newline is detected on the stream.
	def found_terminator(self):
		data = self.buffer
		self.buffer = ''
		command.accept_command(self.parent, data)

	## Shut down the socket and make sure the player's data is saved.
	def handle_close(self):
		if self.parent.location:
			libsigma.report(libsigma.ROOM, "$actor has left the game.", self.parent)
			self.parent.location.characters.remove(self.parent)

		if self.parent in world.players:
			archive.player_save(self.parent)
			world.players.remove(self.parent)

		log("NETWORK", "Client at " + self.addr[0] + " closed connection")
		self.parent.socket = None
		self.close()

	## Overridden member function to handle socket accept (not applicable to Sigma).
	def handle_accept(self):
		pass

## Encapsulates a server socket.
class server_socket(asyncore.dispatcher):
	## Construct the server socket.
	def __init__(self):
		asyncore.dispatcher.__init__(self)

		try:
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
			self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.bind((options["bind_address"], int(options["bind_port"])))
			self.listen(5)
		except:
			log("FATAL", "Error initializing socket")
			sys.exit(1)

	## Handle acceptance of new connections.
	def handle_accept(self):
		accept_socket, address = self.accept()
		log("NETWORK", "Connection received from " + address[0])
		client_socket(accept_socket)
