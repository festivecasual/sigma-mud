from common import *

def register_handlers():
	return	{
		 "say" : say,
		 "emote" : emote,
		 "look" : look
		}

def say(data):
	pass

def emote(data):
	pass

def look(data):
	speaker = data["speaker"]

	import world
	speaker.send_line(world.rooms[options["default_start"]].name)
	speaker.send_line(world.rooms[options["default_start"]].desc)
