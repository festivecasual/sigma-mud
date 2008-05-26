## @package system
#  Handler functions to process and respond to system functions.
#  
#  @ingroup handler

import archive
from libsigma import *

## The mandatory registration function.
def register_handlers():
	return	{
		"quit" : quit,
		"save" : save
		}

## Handle player quit.
#
#  @todo Add a library function to check if this is a player.
def quit(data):
	speaker = data["speaker"]

	speaker.send_line("Goodbye.")
	speaker.socket.handle_close()

## Handle player save.
#
#  @todo Add a library function to check if this is a player.
#  @todo Add a library function for saving players.
def save(data):
	speaker = data["speaker"]

	archive.player_save(speaker)
	data["speaker"].send_line("Game saved.")
