## @package world
#  Contains data structures for objects and constructs within the environment.

import sys, libsigma
from common import *

players = []
rooms = {}
denizens = {}
items = {}

denizens_source = {}
items_source = {}

populators = []
placements = []

## Map exit codes to room objects, reporting any mapping errors.
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

## Map populator references to template denizens, reporting any mapping errors.
def resolve_populators():
	for current in populators:
		if denizens_source.has_key(current.denizen):
			current.denizen = denizens_source[current.denizen]
		elif denizens_source.has_key(current.area + ":" + current.denizen):
			current.denizen = denizens_source[current.area + ":" + current.denizen]
		else:
			log("  *  ERROR", "Unresolved denizen reference: " + current.denizen)
		
		if rooms.has_key(current.target):
			current.target = rooms[current.target]
		elif rooms.has_key(current.area + ":" + current.target):
			current.target = rooms[current.area + ":" + current.target]
		else:
			log("  *  ERROR", "Unresolved target room reference: " + current.target)

## Map placement references to template items, reporting any mapping errors.
def resolve_placements():
	for current in placements:
		if items_source.has_key(current.item):
			current.item = items_source[current.item]
		elif items_source.has_key(current.area + ":" + current.item):
			current.item = items_source[current.area + ":" + current.item]
		else:
			log("  *  ERROR", "Unresolved denizen reference: " + current.item)
		
		if rooms.has_key(current.target):
			current.target = rooms[current.target]
		elif rooms.has_key(current.area + ":" + current.target):
			current.target = rooms[current.area + ":" + current.target]
		else:
			log("  *  ERROR", "Unresolved target room reference: " + current.target)

## Encapsulates an instruction to place a denizen in a certain location.
class populator(object):
	## Construct the populator object.
	#
	#  @param self The active instance.
	#  @param node The XML node describing the populator.
	#  @param area The name of the populator's area (for mapping).
	def __init__(self, node, area):
		## The denizen template to load.
		self.denizen = node.attributes["denizen"].value
		
		## The destination room.
		self.target = node.attributes["target"].value
		
		## The area containing the populator.
		self.area = area
		
		## Any option flags applicable to the populator.
		self.flags = []
		
		## Cache value to track the current instantiated denizen.
		self.instance = None
		
		node.normalize()
		for info_node in node.childNodes:
			if info_node.nodeName == "flag":
				self.flags.append(strip_whitespace(info_node.firstChild.data))

## Encapsulates an instruction to place an item in a certain location.
class placement(object):
	## Construct the placement object.
	#
	#  @param self The active instance.
	#  @param node The XML node describing the placement.
	#  @param area The name of the placement's area (for mapping).
	def __init__(self, node, area):
		## The item template to load.
		self.item = node.attributes["item"].value
		
		## The destination room or object.
		self.target = node.attributes["target"].value
		
		## The area containing the placement.
		self.area = area
		
		## Any option flags applicable to the placement.
		self.flags = []
		
		## Cache value to track the current instantiated item.
		self.instance = None
		
		node.normalize()
		for info_node in node.childNodes:
			if info_node.nodeName == "flag":
				self.flags.append(strip_whitespace(info_node.firstChild.data))

## Encapsulates any entity within the world structure.
class entity(object):
	## Construct the basic default entity.
	#
	#  @param self The active instance.
	def __init__(self):
		## The name of the entity.
		self.name = ""
		
		## The long description of the entity.
		self.description = ""
		
		## Keywords applicable when searching for the entity.
		self.keywords = []
		
		## Contents of the entity.
		self.contents = []
		
		## Capacity of the entity to hold contents.
		self.capacity = 0
		
		## The entity's room location.
		self.location = ""

## Encapsulates a tangible object within the world.
class item(entity):
  ## Construct the item from XML.
  #
  #  @param self The active instance.
  #  @param node The XML node describing the item.
  def __init__(self, node):
    entity.__init__(self)
    
    node.normalize()
    for info_node in node.childNodes:
   		if info_node.nodeName == "name":
			self.name = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
		elif info_node.nodeName == "keywords":
			self.keywords.extend(strip_whitespace(info_node.firstChild.data).lower().split())
		elif info_node.nodeName == "short":
			self.short = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
		elif info_node.nodeName == "desc":
			self.desc = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))

## Encapsulates a room within the world.
class room(entity):
	## Construct the room from XML.
	#
	#  @param self The active instance.
	#  @param ref The reference code for the room.
	#  @param node The XML node describing the room.
	def __init__(self, ref, node):
		entity.__init__(self)
		self.location = ref

		self.characters = []
		self.keywords = ["room"]
		self.exits = [None] * NUM_DIRS
		self.foci = {}
		
		self.capacity = -1

		node.normalize()
		for info_node in node.childNodes:
			if info_node.nodeName == "name":
				self.name = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "desc":
				self.desc = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "focus":
				if not info_node.attributes.has_key("name"):
					log("FATAL", "Error in <focus /> tag within <room />")
					sys.exit(1)
				name = info_node.attributes["name"].value
				description = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
				
				self.foci[name] = description
			elif info_node.nodeName == "exit":
				if (not info_node.attributes.has_key("dir")) or (not info_node.attributes.has_key("target")):
					log("FATAL", "Error in <room /> tag")
					sys.exit(1)
				dir = libsigma.txt2dir(info_node.attributes["dir"].value)
				if dir == -1:
					log("FATAL", "Bad exit direction: " + info_node.attributes["dir"].value)
					sys.exit(1)
				self.exits[dir] = info_node.attributes["target"].value

	## Return the area portion of the room's location code.
	#
	#  @param self The active instance.
	def get_area(self):
		return self.location[:self.location.find(":")]

	## Provide a property structure to return the room's area.
	area = property(get_area)

## Encapsulates an abstract denizen or player within the world.
class character(entity):
	## Construct the abstract character.
	#
	#  @param self The active instance.
	def __init__(self):
		entity.__init__(self)

		self.state = STATE_NULL

	## Abstract function to simulate sending a prompt string to a player.
	#
	#  @param self The active instance.
	def send_prompt(self): pass

	## Abstract function to send data to the character.
	#
	#  @param self The active instance.
	#  @param s The data to send.
	def send(self, s = ""): pass

	## Abstract convenience function to send a line of data to the character.
	#
	#  @param self The active instance.
	#  @param s The data to send.
	#  @param breaks The number of breaks to send, following \c s.
	def send_line(self, s = "", breaks = 1): pass

## Encapsulates a denizen (non-playing character) within the world.
class denizen(character):
	## Construct the denizen.
	#
	#  @param self The active instance.
	#  @param node The XML node describing the denizen.
	def __init__(self, node):
		character.__init__(self)

		self.state = STATE_PLAYING
		
		node.normalize()
		for info_node in node.childNodes:
			if info_node.nodeName == "name":
				self.name = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "keywords":
				self.keywords.extend(strip_whitespace(info_node.firstChild.data).lower().split())
			elif info_node.nodeName == "short":
				self.short = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "desc":
				self.desc = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))

## Encapsulates a player (with a socket connection) within the world.
class player(character):
	## Construct the player.
	#
	#  @param self The active instance.
	#  @param s The player's socket object.
	def __init__(self, s):
		character.__init__(self)

		self.proto = None
		self.password = None
		self.socket = None
		self.state = STATE_INIT

		self.socket = s
		self.send_prompt()
	
	## Send a prompt to the player.
	#
	#  @param self The active instance.
	def send_prompt(self):
		self.socket.push(prompts[self.state])

		if (self.state == STATE_INIT):
			self.state = STATE_NAME
			self.send_prompt()

	## Send data to the player.
	#
	#  @param self The active instance.
	#  @param s The data to send.
	def send(self, s = ""):
		self.socket.push(s)

	## Convenience function to send a line of data to the player.
	#
	#  @param self The active instance.
	#  @param s The data to send.
	#  @param breaks The number of breaks to send, following \c s.
	def send_line(self, s = "", breaks = 1):
		self.send(s)
		self.send("\r\n" * breaks)

	## Overloaded function to return search keywords for the player.
	#
	#  @param self The active instance.
	def get_keywords(self):
		return [self.name.lower()]
	
	## Blank function to complete the property() assignment to keywords.
	#
	#  @param self The active instance.
	def set_keywords(self, data):
		pass
	
	keywords = property(get_keywords, set_keywords)
	
	## Returns a short description of the player.
	#
	#  @param self The active instance.
	def get_short(self):
		return self.name + " is here."

	short = property(get_short)
