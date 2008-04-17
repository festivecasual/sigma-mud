import sys, libsigma
from common import *

players = []

rooms = {}
denizens = {}

def resolve_links():
	for current in rooms.values():		
		for i in range(NUM_DIRS):
			if not current.exits[i]:
				continue

			if rooms.has_key(current.exits[i]):
				current.exits[i] = rooms[current.exits[i]]
			elif rooms.has_key(current.area + ":" + current.exits[i]):
				current.exits[i] = rooms[current.area + ":" + current.exits[i]]
			else:
				log("  *  ERROR", "Unresolved room exit linkage: " + current.exits[i] + " (" + current.location + ")")
				current.exits[i] = None

class entity(object):
	def __init__(self):
		self.name = ""
		self.description = ""
		self.keywords = []
		self.contents = []
		self.location = ""

class item(entity):
  def __init__(self, node):
    entity.__init__(self)

class room(entity):
	def __init__(self, ref, node):
		entity.__init__(self)
		self.location = ref

		self.characters = []
		self.keywords = ["room"]
		self.exits = [None] * NUM_DIRS

		node.normalize()
		for info_node in node.childNodes:
			if info_node.nodeName == "name":
				self.name = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "desc":
				self.desc = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "exit":
				if (not info_node.attributes.has_key("dir")) or (not info_node.attributes.has_key("target")):
					log("FATAL", "Error in <room /> tag")
					sys.exit(1)
				dir = libsigma.txt2dir(info_node.attributes["dir"].value)
				if dir == -1:
					log("FATAL", "Bad exit direction: " + info_node.attributes["dir"].value)
					sys.exit(1)
				self.exits[dir] = info_node.attributes["target"].value

	def get_area(self):
		return self.location[:self.location.find(":")]

	area = property(get_area)

class character(entity):
	def __init__(self):
		entity.__init__(self)

		self.state = STATE_NULL

	def send_prompt(self): pass

	def send(self, s = ""): pass

	def send_line(self, s = "", breaks = 1): pass
	
	def get_keywords(self):
		return [self.name.lower()]
	
	def set_keywords(self, new_keywords):
		pass
	
	keywords = property(get_keywords, set_keywords)

class denizen(character):
	def __init__(self, node):
		character.__init__(self)

		self.state = STATE_PLAYING
		
		node.normalize()
		for info_node in node.childNodes:
			if info_node.nodeName == "name":
				self.name = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "keywords":
				self.keywords.extend(strip_whitespace(info_node.firstChild.data).split())
			elif info_node.nodeName == "short":
				self.short = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "desc":
				self.desc = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))

class player(character):
	def __init__(self, s):
		character.__init__(self)

		self.proto = None
		self.password = None
		self.socket = None
		self.state = STATE_INIT

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
	
	def get_short(self):
		return self.name + " is here."

	short = property(get_short)
