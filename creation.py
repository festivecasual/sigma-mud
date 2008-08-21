## @package creation
#  Defines the character class and race framework.

from common import *

## Holds all available character classes
classes = {}

## Holds all available character races
races = {}

class character_class(object):
	def __init__(self, node):
		node.normalize()
		for info_node in node.childNodes:
			if info_node.nodeName == "name":
				self.name = strip_whitespace(info_node.firstChild.data)
			elif info_node.nodeName == "desc":
				self.desc = wordwrap(strip_whitespace(info_node.firstChild.data))
			elif info_node.nodeName == "background":
				self.background = wordwrap(strip_whitespace(info_node.firstChild.data))
			elif info_node.nodeName == "stats":
				pass
			elif info_node.nodeName == "paths":
				pass
			elif info_node.nodeName == "skills":
				pass

