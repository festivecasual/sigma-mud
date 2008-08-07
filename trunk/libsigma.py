## @package libsigma
#  Designer-facing utility functions.

import traceback, sys, command
from string import Template
from common import *

## Decorator function to be attached to all handlers.
#
#  "Marks" a designer function as a handler for import.
#
#  @param function The function to decorate.
def handler(function):
	function.__handler__ = 'handler'
	return function

## Run a function within an error-trapped environment.
#
#  The safe_mode function is used to trap errors in non-essential
#  (usually designer-generated) code, to avoid a forced quit and stack
#  trace in normal game operation.
#
#  @param function The function to execute.
#  @param args The arguments to pass to the function.
def safe_mode(function, *args):
	ret = False

	if options['debug'] == 'yes':
		return function(*args)
	
	try:
		ret = function(*args)
	except:
		tb = sys.exc_info()[2]
		last = traceback.extract_tb(tb)[-1]
		log("  *  ERROR", last[0] + ":" + str(last[1]) + " (" + last[2] + ")")
	
	return ret

## Provide a basic means of producing log text within designer code.
#
#  @param text The text to include in the log entry.
def alert(text):
	log("  *  ALERT", text)

## Test if a character object (or any other object within Sigma) is a Player.
#
#  @param object The object to test.
def is_player(object):
	return hasattr(object, "socket")

## Convert a text-based direction specifier to a mapped direction code.
#
#  @param text The text to convert.
#  @return The direction code, or -1 to indicate that \c text was invalid.
#
#  @sa This function's inverse is dir2txt.
def txt2dir(text):
	for i in range(len(dir_match_dir)):
		if dir_match_txt[i].startswith(text):
			return dir_match_dir[i]

	return -1

## Convert a direction code to a text-based identifier.
#
#  @param dir The direction code to convert.
#  @return The plain-text direction.
#
#  @sa This function's inverse is txt2dir.
def dir2txt(dir):
	for i in range(len(dir_match_dir)):
		if dir_match_dir[i] == dir:
			return dir_match_txt[i]
	
	return ''

## Generate a list of all available exits in the room.
#
#  @param room The room to analyze.
#  @return A list object with all available exits in \c room.
def exits(room):
	result = []

	for i in range(len(room.exits)):
		if room.exits[i]:
			result.append(i)
	
	return result

## Move a character into a room.
#
#  @param character The character to relocate.
#  @param room The destination room.
def enter_room(character, room):
	if character.location:
		character.location.characters.remove(character)

	room.characters.append(character)
	character.location = room

## Check if a name maps to a character in a room.
#
#  @param name The name to search for.
#  @param room The room to search.
#  @param self_character Character to return for "self" if desired.
#  @return The character object, if found.  Otherwise, None.
def character_in_room(name, room, self_character = None):
	for search in room.characters:
		for keyword in search.keywords:
			if keyword.startswith(name):
				return search

	if "self".startswith(name):
		return self_character
	
	return None

## Check if a name maps to an item in a location.
#
#  @param name The name to search for.
#  @param room The room to search.
#  @return The item, if found.  Otherwise, None.
def item_in_room(name, room):
	for search in room.contents:
		for keyword in search.keywords:
			if keyword.startswith(name):
				return search

	return None

## Check if a name maps to a focus in a location.
#
#  @param name The name to search for.
#  @param room The room to search.
#  @return The focus text, if found.  Otherwise, None.
def focus_in_room(name, room):
	for key, text in room.foci.items():
		if key.startswith(name):
			return text
	
	return None

## Move an item from one collection (inventory, room) to another.
#
#  @param item The item to relocate.
#  @param from_collection The collection the item is currently within.
#  @param to_collection The collection the item is to be within.
#  @return Boolean indication of success.
def transfer_item(item, from_collection, to_collection):
	if item in from_collection:
		to_collection.append(item)
		from_collection.remove(item)
		return True
	else:
		return False

## Force a simulated command into the command queue.
#
#  This function is generally used to type a command for a denizen to execute.
#  It is also useful for queueing a default command (i.e., "look") as a result
#  of another action (i.e., "go").
#
#  @param character The character that receives the simulated-typed command.
#  @param text The text to simulate-type.
#
#  @sa Use run_command to execute the command immediately, rather than queueing it for next processing.
def queue_command(character, text):
	command.accept_command(character, text)

## Force a simulated command to be run immediately.
#
#  @param character The character that receives the simulated-typed command.
#  @param text The text to simulate-type.
#
#  @sa Use queue_command to queue the command, rather than executing it immediately.
def run_command(character, text):
	if not command.run_command(character, text):
		log("  *  ERROR", "Command <" + text + "> unsuccessful")

## Report function recipient: the acting player.
SELF =  1
## Report function recipient: the acting player's room.
ROOM =  2
## Report function recipient: the acting player's nearby rooms.
NEAR =  4 # TODO
## Report function recipient: the acting player's area (excluding nearby rooms).
AREA =  8 # TODO
## Report function recipient: the entire game (excluding the active area).
GAME = 16 # TODO

## The master function to send formatted, conjugated text to arbitrary groups of characters.
#
#  @param recipients One of the recipient constants defined within libsigma.py.
#  @param template The template string through which the message is formatted.
#  @param actor The subject of the action report.
#  @param verbs A tuple of conjugated verbs
#  @param direct The direct object of the action report.
#  @param indirect The indirect object of the action report.
#
#  @todo Fully define all recipient constants in libsigma.py.
#  @todo Gender awareness.
def report(recipients, template, actor, verbs = None, direct = None, indirect = None):
	out = ""
	s = Template(template)
	
	mapping = {
		"actor" : actor.name
		}
	self_mapping = {
		"actor" : "you"
		}
	
	if verbs:
		mapping["verb"] = verbs[1]
		self_mapping["verb"] = verbs[0]

	if direct:
		if direct != actor:
			mapping["direct"] = direct.name
			self_mapping["direct"] = direct.name
		else:
			mapping["direct"] = "itself"
			self_mapping["direct"] = "yourself"
	
	if indirect:
		if indirect != actor:
			mapping["indirect"] = indirect.name
			self_mapping["indirect"] = indirect.name
		else:
			mapping["indirect"] = "itself"
			self_mapping["indirect"] = "yourself"

	if SELF & recipients:
		out = s.safe_substitute(self_mapping)
		out = out[0].upper() + out[1:]
		actor.send_line(out)

	out = s.safe_substitute(mapping)
	out = out[0].upper() + out[1:]

	if ROOM & recipients:
		for character in actor.location.characters:
			if character != actor:
				character.send_line("")
				if character == direct:
					out_special = s.safe_substitute(mapping, direct = "you")
					out_special = out_special[0].upper() + out_special[1:]
					character.send_line(out_special)
				elif character == indirect:
					out_special = s.safe_substitute(mapping, indirect = "you")
					out_special = out_special[0].upper() + out_special[1:]
					character.send_line(out_special)
				else:
					character.send_line(out)

	return out