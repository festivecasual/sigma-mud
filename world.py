from common import *

class entity:
	def __init__(self):
		self.name = ''
		self.desc_short = ''
		self.desc_long = ''

		self.contents = []

class character(entity):
	def __init__(self):
		entity.__init__(self)

		self.state = STATE_NULL

	def send_prompt(self): pass

	def send(self, s = ""): pass

	def send_line(self, s = ""): pass

class denizen(character):
	def __init__(self):
		character.__init__(self)

		self.state = STATE_PLAYING

class player(character):
	def __init__(self, s):
		character.__init__(self)

		self.proto = None
		self.password = None
		self.socket = s
		self.state = STATE_INIT_NAME

		self.send_prompt()

	def send_prompt(self):
		self.socket.push(prompts[self.state])

		if (self.state == STATE_INIT_NAME):
			self.state = STATE_NAME
			self.send_prompt()

	def send(self, s = ""):
		self.socket.push(s)

	def send_line(self, s = ""):
		self.send(s)
		self.send("\r\n")
