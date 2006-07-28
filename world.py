from common import *

players = []

rooms = {}
locations = {}

class entity:
	def __init__(self): pass

	name = ''
	keywords = ['']
	description = ''
	contents = []
	location = ''

class room(entity):
	def __init__(self, ref, node):
		entity.__init__(self)
		location = ref

		node.normalize()
		for info_node in node.childNodes:
			if info_node.nodeName == "name":
				self.name = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "desc":
				self.desc = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))

	keywords = ['room']

class character(entity):
	def __init__(self):
		entity.__init__(self)

	def send_prompt(self): pass

	def send(self, s = ""): pass

	def send_line(self, s = "", breaks = 1): pass

	def get_keywords(self):
		return [self.name.lower()]

	state = STATE_NULL
	keywords = property(get_keywords)

class denizen(character):
	def __init__(self):
		character.__init__(self)

	state = STATE_PLAYING

class player(character):
	def __init__(self, s):
		character.__init__(self)

		self.socket = s
		self.send_prompt()

	def send_prompt(self):
		self.socket.push(prompts[self.state])

		if (self.state == STATE_INIT):
			self.state = STATE_NAME
			self.send_prompt()

	def send(self, s = ""):
		self.socket.push(s)

	def send_line(self, s = "", breaks = 1):
		self.send(s)
		self.send("\r\n" * breaks)

	state = STATE_INIT
	proto = None
	password = None
	socket = None
