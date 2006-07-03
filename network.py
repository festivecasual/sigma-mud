import asyncore, asynchat, socket, sys
import structs, command
from common import *

class client_socket(asynchat.async_chat):
	def __init__(self, connection):
		asynchat.async_chat.__init__(self, connection)
		self.buffer = ''
		self.set_terminator('\n')
		self.parent = structs.player()

	def collect_incoming_data(self, data):
		self.buffer += data.replace('\r', '')

	def found_terminator(self):
		data = self.buffer
		self.buffer = ''
		command.accept_command(self.parent, data)

	def handle_close(self):
		log("NETWORK", "Client closed connection")
		self.close()

	def handle_accept(self):
		pass


class server_socket(asyncore.dispatcher):
	def __init__(self):
		asyncore.dispatcher.__init__(self)

		try:
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
			self.bind(('', 4000))
			self.listen(5)
		except:
			log("FATAL", "Error initializing socket")
			sys.exit(1)

	def handle_accept(self):
		accept_socket, address = self.accept()
		log("NETWORK", "Connection received from " + address[0])
		client_socket(accept_socket)
