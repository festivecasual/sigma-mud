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

emote_mappings = {
	"wave" : ("$actor $verb.", "$actor $verb at $direct.", ("wave", "waves"))
	}

def emote(data):
	speaker = data["speaker"]
	tail = data["tail"]
	mapped = data["mapped"]
	args = data["args"]

	if mapped == "emote":
		out = report(ROOM, "$actor " + tail + ".", speaker)
		speaker.send_line(out)
		return

	elif emote_mappings.has_key(mapped):
		nodirect, direct, verbs = emote_mappings[mapped]
		
		if len(args) > 1:
			if not direct:
				speaker.send_line("You can't do that.")
				return
			target = character_in_room(speaker, args[1])
			if target:
				report(SELF | ROOM, direct, speaker, verbs, target)
				return
			else:
				report(SELF, "$verb at whom?", speaker, verbs)
				return
		else:
			if nodirect:
				report(SELF | ROOM, nodirect, speaker, verbs)
				return
			else:
				alert("Emote command " + mapped + " does not have a usable form")
				return

	else:
		speaker.send_line("I don't understand.")
		alert("Emote command " + mapped + " references an unknown emote_mapping")

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
