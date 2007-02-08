from libsigma import *

def register_handlers():
	return	{
		"say" : say,
		"emote" : emote,
		"look" : look,
		"go" : go
		}

def say(data):
	speaker = data["speaker"]
	tail = data["tail"]
	
	report(SELF | ROOM, "$actor $verb, '" + tail + "'", speaker, ("say", "says"))

def emote(data):
	speaker = data["speaker"]
	tail = data["tail"]
	
	out = report(ROOM, "$actor " + tail + ".", speaker)
	speaker.send_line(out)

def look(data):
	speaker = data["speaker"]

	speaker.send_line(speaker.location.name)
	speaker.send_line(speaker.location.desc)

	speaker.send("Exits: ")
	for dir in exits(speaker.location):
		speaker.send(dir2txt(dir) + " ")
	speaker.send_line("")
	
	for character in speaker.location.characters:
		if character != speaker:
			speaker.send_line(character.name + " is here.")

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
		report(ROOM, "$actor has left the room.", speaker)
		enter_room(speaker, speaker.location.exits[dir])
		report(ROOM, "$actor has entered the room.", speaker)
		run_command(speaker, "look")
	else:
		speaker.send_line("There is no exit in that direction.")
