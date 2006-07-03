from common import *

class entity:
	def __init__(self):
		self.name = ''
		self.desc_short = ''
		self.desc_long = ''

class character(entity):
	def __init__(self):
		entity.__init__(self)

		self.state = STATE_NULL

class denizen(character):
	def __init__(self):
		character.__init__(self)

		self.state = STATE_PLAYING

class player(character):
	def __init__(self):
		character.__init__(self)

		self.state = STATE_NAME
