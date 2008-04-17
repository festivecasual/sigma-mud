import traceback, sys, command
from string import Template
from common import *

def safe_mode(function, *args):
	ret = False

	try:
		ret = function(*args)
	except:
		tb = sys.exc_info()[2]
		last = traceback.extract_tb(tb)[-1]
		log("  *  ERROR", last[0] + ":" + str(last[1]) + " (" + last[2] + ")")

	return ret

def alert(text):
	log("  *  ALERT", text)

def txt2dir(text):
	for i in range(len(dir_match_dir)):
		if dir_match_txt[i].startswith(text):
			return dir_match_dir[i]

	return -1

def dir2txt(dir):
	for i in range(len(dir_match_dir)):
		if dir_match_dir[i] == dir:
			return dir_match_txt[i]
	
	return ''

def exits(room):
	result = []

	for i in range(NUM_DIRS):
		if room.exits[i]:
			result.append(i)
	
	return result

def enter_room(character, room):
	if character.location:
		character.location.characters.remove(character)

	room.characters.append(character)
	character.location = room

def character_in_room(character, name):
	for search in character.location.characters:
		for keyword in search.get_keywords():
			if keyword.lower().startswith(name.lower()):
				return search

	if "self".startswith(name):
		return character
	
	return None

def queue_command(character, text):
	command.accept_command(character, text)

def run_command(character, text):
	if not command.run_command(character, text):
		log("  *  ERROR", "Command <" + text + "> unsuccessful")

SELF =  1
ROOM =  2
NEAR =  4 # TODO
AREA =  8 # TODO
GAME = 16 # TODO

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
			mapping["direct"] = "itself" # TODO
			self_mapping["direct"] = "yourself"
	
	if indirect:
		if indirect != actor:
			mapping["indirect"] = indirect.name
			self_mapping["indirect"] = indirect.name
		else:
			mapping["indirect"] = "itself" # TODO
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
