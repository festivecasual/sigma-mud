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
	"cackle" : ("$actor $verb like a maniac!", "$actor $verb at $direct!", ("cackle", "cackles")),
	"grin" : ("$actor $verb.", "$actor $verb at $direct.", ("grin", "grins")),
	"laugh" : ("$actor $verb.", "$actor $verb at $direct.", ("laugh", "laughs")),
	"smile" : ("$actor $verb.", "$actor $verb at $direct.", ("smile", "smiles")),
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
				report(SELF, "They're not here.", speaker)
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
		#if direction >= 0 and speaker.location.exits[direction]:
		if direction >= 0 and direction in open_exits(speaker.location):
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
	for code in open_exits(speaker.location):
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

	direction = -1

	if "go".startswith(args[0]) and len(args) == 2:
		direction = txt2dir(args[1])
	elif len(args) == 1:
		direction = txt2dir(args[0])

	if direction == -1:
		speaker.send_line("Where do you want to go?")
	elif speaker.location.can_character_go(direction):			
		if speaker.location.altmsg[direction]!=None: ## checks first for any alternate messaging
			report(ROOM, "$actor just went " + speaker.location.altmsg[direction]  + "." , speaker)
		elif dir2txt(direction) =="leave":
			report(ROOM, "$actor just went out.", speaker)
		elif dir2txt(direction) =="enter":
			report(ROOM, "$actor just went in.", speaker)
		else:
			report(ROOM, "$actor just went " + dir2txt(direction) + ".", speaker)        
		enter_room(speaker, speaker.location.exits[direction])
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
		speaker.send_line(args[0].title() + " what?")
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

## Transfer item from character to character
@handler
def give(data):
	speaker = data["speaker"]
	args = data["args"]
	
	if len(args) == 2:
		speaker.send_line("Give to whom?")
		return
	elif len(args) != 3:
		speaker.send_line("You can't do that.")
		return
	
	target = None
	for item in speaker.contents:
		for keyword in item.keywords:
			if keyword.startswith(args[1]):
				target = item
				break
	
	if not target:
		speaker.send_line("You don't have that.")
		return
	
	recipient = character_in_room(args[2], speaker.location, speaker)
	if not recipient:
		speaker.send_line("They're not here.")
		return
	
	if recipient == speaker:
		speaker.send_line("You cannot give to yourself.")
		return
	
	transfer_item(target, speaker.contents, recipient.contents)
	report(SELF | ROOM, "$actor $verb $direct to $indirect.", speaker, ("give", "gives"), target, recipient)

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
@ handler
def open(data):
	speaker=data["speaker"]
	args=data["args"]
	
	if len(args) < 2:
		speaker.send_line(str(args[0]).title() + " what?")
	else: ## support currently only for doors! Open will most likely also deal with containers later
   		direction=txt2dir(args[1])
   	 	if(speaker.location.is_door_closed(direction)):
	   	  	speaker.location.open_door(direction)
	   	   	report(SELF | ROOM, "$actor $verb the door.", speaker, ("open","opens"))
	 	else:
	 		speaker.send_line("You can't open that.")

@ handler
def close(data):
	speaker=data["speaker"]
	args=data["args"]
	
	if len(args) < 2:
		speaker.send_line(str(args[0]).title() + " what?")
	else: ## support currently only for doors! Close will most likely also deal with containers later
   		direction=txt2dir(args[1])
   	 	if(not speaker.location.is_door_closed(direction) and speaker.location.doors[direction]!=None):
	   	  	speaker.location.close_door(direction)
	   	   	report(SELF | ROOM, "$actor $verb the door.", speaker, ("close","closes"))
	 	else: 
	 		speaker.send_line("You can't close that.")