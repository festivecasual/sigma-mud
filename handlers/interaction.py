## @package interaction
#  Handler functions to process and respond to interactions between the character and the world.
#  
#  @ingroup handler

from libsigma import *

## Process character conversation.
@handler
def say(data):
	speaker = data["speaker"]
	tail = data["tail"]
	
	report(SELF | ROOM, "$actor $verb, '" + tail + "'", speaker, ("say", "says"))

## Used by the emote handler to produce the necessary action strings.
emote_mappings = {
	"laugh" : ("$actor $verb.", "$actor $verb at $direct.", ("laugh", "laughs")),
	"slap" : ("", "$actor $verb $direct.", ("slap", "slaps")),
	"wave" : ("$actor $verb.", "$actor $verb at $direct.", ("wave", "waves")),
	"wink" : ("$actor $verb.", "$actor $verb at $direct.", ("wink", "winks"))
	}

## Process character emotion.
@handler
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
			target = character_in_room(args[1], speaker.location, speaker)
			if target:
				report(SELF | ROOM, direct, speaker, verbs, target)
				return
			else:
				report(SELF, "They are not here.", speaker)
				return
		else:
			if nodirect:
				report(SELF | ROOM, nodirect, speaker, verbs)
				return
			else:
				report(SELF, "You must specify a target to $verb.", speaker, verbs)
				return

			alert("Emote command <" + mapped + "> does not have a usable form")
			return

	else:
		speaker.send_line("I don't understand.")
		alert("Emote command <" + mapped + "> references an unknown emote_mapping")

## Process character observation of world objects (items, players, denizens, etc.).
@handler
def look(data):
	speaker = data["speaker"]
	args = data["args"]

	if len(args) > 1:
		objective = args[1]
		
		if objective == "self":
			speaker.send_line("You see yourself.")  # TODO
			return

		direction = txt2dir(objective)
		if direction >= 0 and speaker.location.exits[direction]:
			speaker.send_line("You see " + speaker.location.exits[direction].name + " in that direction.")
			return
		
		target = character_in_room(objective, speaker.location, speaker)
		if target:
			speaker.send_line(target.desc)
			return
		
		target = item_in_room(objective, speaker.location)
		if target:
			speaker.send_line(target.desc)
			return
		
		focus_text = focus_in_room(objective, speaker.location)
		if focus_text:
			speaker.send_line(focus_text)
			return

	speaker.send_line(speaker.location.name)
	speaker.send_line(speaker.location.desc)

	speaker.send("Exits: ")
	for code in exits(speaker.location):
		speaker.send(dir2txt(code) + " ")
	speaker.send_line("")
	
	for character in speaker.location.characters:
		if character != speaker:
			speaker.send_line(character.short)
	
	for item in speaker.location.contents:
		speaker.send_line(item.short)

## Process character movement.
@handler
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

## Process item acquisition.
#
#  @todo Containers within inventory (len(args) == 3)
#  @todo Detect failures during item transfers (weight limits, etc.)
@handler
def get(data):
	speaker = data["speaker"]
	args = data["args"]
	
	if len(args) == 1:
		speaker.send_line("Get what?")
		return
	elif len(args) != 2:
		speaker.send_line("You can't do that.")
		return
	
	item = item_in_room(args[1], speaker.location)
	if item:
		transfer_item(item, speaker.location.contents, speaker.contents)
		report(SELF | ROOM, "$actor $verb $direct.", speaker, ("pick up", "picks up"), item)
	else:
		speaker.send_line("You can't find it.")

## Process item drops.
@handler
def drop(data):
	speaker = data["speaker"]
	args = data["args"]
	
	if len(args) == 1:
		speaker.send_line("Drop what?")
		return
	elif len(args) != 2:
		speaker.send_line("You can't do that.")
		return
	
	for item in speaker.contents:
		for keyword in item.keywords:
			if keyword.startswith(args[1]):
				transfer_item(item, speaker.contents, speaker.location.contents)
				report(SELF | ROOM, "$actor $verb $direct.", speaker, ("drop", "drops"), item)
				return
	
	speaker.send_line("You don't have that.")

## Display a list of inventory.
@handler
def inventory(data):
	speaker = data["speaker"]
	
	speaker.send_line("You are carrying:")
	
	if len(speaker.contents) == 0:
		speaker.send_line("    nothing");
	else:
		for item in speaker.contents:
			speaker.send_line("   " + item.name)
