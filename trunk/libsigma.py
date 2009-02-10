## @package libsigma
#  Designer-facing utility functions.

import traceback, sys, command, time, math
from string import Template

import task
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

## Provide a "NOOP" function for empty callbacks.
def noop():
	pass

## Provides a basic object infrastructure for inserting tasks.
class inserted_task(object):
	## Construct the default inserted task.
	def __init__(self):
		self.task_init = noop
		self.task_execute = noop
		self.task_deinit = noop

## Insert a task with a specified TTL into the tasks structure
#
#  @param name The identifier for the task.
#  @param task_function The function to insert.
#  @param interval Time space between each function execution (in seconds).
#  @param ttl The lifetime (number of intervals) for the task.
def insert_task(name, task_function, interval, ttl = -1):
	# Construct a dummy "module" for the task
	task_module = inserted_task()
	task_module.task_execute = task_function
	task.tasks[name + '_' + str(time.time())] = (task_module, time.time(), interval, ttl)

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

## Convert a text-based worn item specifier to a mapped worn item code.
#
#  @param text The text to convert.
#  @return The worn item code, or -1 to indicate that \c text was invalid.
#
#  @sa This function's inverse is worn2txt.
def txt2worn(text):
	for i in range(len(worn_match_val)):
		if worn_match_txt[i].startswith(text):
			return worn_match_val[i]

	return -1

## Convert a worn item code to a text-based identifier.
#
#  @param worn The worn item code to convert.
#  @return The plain-text direction.
#
#  @sa This function's inverse is txt2worn.
def worn2txt(worn):
	for i in range(len(worn_match_val)):
		if worn_match_val[i] == worn:
			return worn_match_txt[i]
	
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
#Generates a list of all exits that are not closed
def open_exits(room):
	result = []
	
	for i in range(len(room.exits)):
		if room.exits[i]:
			if(not room.is_door_closed(i)):
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

## Generate a phi (asymptotic percentage statistic) function.
#
#  @param stat_initial The value of phi at L = 0
#  @param level_maturity The L value for which phi = 0.95
def phi(stat_initial, level_maturity):
	alpha = math.exp((-1 * math.log(0.05 / (1 - stat_initial))) / level_maturity)
	return lambda L: stat_initial + (1 - stat_initial) * (1 - alpha ** (-1 * L))

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

## Determines if for a particular worn item type if a character is at capacity
def at_capacity(character,worn_spot): 
	count=0
	for worn_item in character.worn_items:
		if worn_item.worn_position == worn_spot:
			count+=1
	return count >= worn_limit[worn_spot]

## adds and removes allocation points
def add_points(character,number):
	character.points_to_allocate = character.points_to_allocate + number
	return True
def remove_points(character,number):
	character.points_to_allocate = character.points_to_allocate - number
	if character.points_to_allocate < 0:
		character.points_to_allocate = 0
	return True

# function to raise stats. Any restrictions on whether a stat should be able to be raised
# can be coded here.
def raise_stat(character,stat, number):
		character.stats[stat] = character.stats[stat] + number
		return True
	
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
			mapping["direct"] = pronoun_reflexive[direct.gender]
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
		for search in actor.location.characters:
			if search != actor:
				search.send_line("")
				if search == direct:
					out_special = s.safe_substitute(mapping, direct = "you")
					out_special = out_special[0].upper() + out_special[1:]
					search.send_line(out_special)
				elif search == indirect:
					out_special = s.safe_substitute(mapping, indirect = "you")
					out_special = out_special[0].upper() + out_special[1:]
					search.send_line(out_special)
				else:
					search.send_line(out)
	if NEAR & recipients:
		announce(NEAR, actor.location, out)
	
	return out

# room based report. Does not originate at a person, rather at a room.
# Since the room is the target, this is the messaging that is used
# only when the message is uniformly presented to all in the room
# with this implementation
def announce(recipients,room, message):
	
	if(ROOM & recipients):
		for all in room.characters:
			all.send_line(message)
	if(NEAR & recipients): 
		for exit in room.exits:         #assuming that NEAR does not require open doors. Good assumption?
			if exit != None:
				announce(ROOM, exit, message)
	#if(AREA & recipients):
	 
	#if(GAME & recipients):				
	return
