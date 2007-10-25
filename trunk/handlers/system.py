import archive
from libsigma import *

def register_handlers():
	return	{
		"quit" : quit,
		"save" : save
		}

def quit(data):
	speaker = data["speaker"]

	# TODO: Add a library function to check if this is a player
	speaker.send_line("Goodbye.")
	speaker.socket.handle_close()

def save(data):
	speaker = data["speaker"]

	# TODO: Add a library function to check if this is a player
	# TODO: Add a library function for saving players
	archive.player_save(speaker)
	data["speaker"].send_line("Game saved.")
