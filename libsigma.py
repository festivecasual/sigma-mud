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

def queue_command(character, text):
	command.accept_command(character, text)

def run_command(character, text):
	if not command.run_command(character, text):
		log("  *  ERROR", "Command <" + text + "> unsuccessful")

SELF = 1
ROOM = 2
AREA = 4
GAME = 8

def report(recipients, template, actor, direct = None, indirect = None):
	s = Template(template)
	mapping = {
		"actor" : actor.name
		}

	if direct:
		mapping["direct"] = direct.name
	
	if indirect:
		mapping["indirect"] = indirect.name

	if SELF & recipients:
		out = s.safe_substitute(mapping, actor = "you")
		out = out[0].upper() + out[1:]
		actor.send_line(out)
