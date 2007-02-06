import traceback, sys
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

def enter_room(character, room):
	if character.location:
		character.location.characters.remove(character)

	room.characters.append(character)
	character.location = room
