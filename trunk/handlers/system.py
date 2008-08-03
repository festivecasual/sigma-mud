## @package system
#  Handler functions to process and respond to system functions.
#  
#  @ingroup handler

import archive
from libsigma import *

## Handle player quit.
@handler
def quit(data):
	speaker = data["speaker"]

	if is_player(speaker):
		speaker.send_line("Goodbye.")
		speaker.socket.handle_close()
	else:
		speaker.send_line("Only players can quit.")

## Handle player save.
@handler
def save(data):
	speaker = data["speaker"]

	if is_player(speaker):
		archive.player_save(speaker)
		data["speaker"].send_line("Game saved.")
	else:
		speaker.send_line("Only players can save.")
