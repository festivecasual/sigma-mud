from libsigma import *

def register_handlers():
	return	{
		 "say" : say,
		 "emote" : emote,
		 "look" : look,
		 "go" : go
		}

def say(data):
	pass

def emote(data):
	pass

def look(data):
	speaker = data["speaker"]

	import world
	speaker.send_line(speaker.location.name)
	speaker.send_line(speaker.location.desc)
	
	speaker.send("Exits: ")
	for dir in exits(speaker.location):
		speaker.send(dir2txt(dir) + " ")
	speaker.send_line("")

def go(data):
	log("GO", "GO")
