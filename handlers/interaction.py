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

	speaker.send_line(speaker.location.name)
	speaker.send_line(speaker.location.desc)

	speaker.send("Exits: ")
	for dir in exits(speaker.location):
		speaker.send(dir2txt(dir) + " ")
	speaker.send_line("")

def go(data):
	speaker = data["speaker"]
	args = data["args"]

	dir = -1

	if "go".startswith(args[0]) and len(args) == 2:
		dir = txt2dir(args[1])
	elif len(args) == 1:
		dir = txt2dir(args[0])

	if dir == -1:
		speaker.send_line("Where do you want to go?")
	elif speaker.location.exits[dir]:
		enter_room(speaker, speaker.location.exits[dir])
	else:
		speaker.send_line("There is no exit in that direction.")
