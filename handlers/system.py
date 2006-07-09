from common import *

def register_handlers():
	return	{
		 "quit" : quit,
		 "save" : save
		}

def quit(data):
	# TODO: Add a library function to check if this is a player...
	data["speaker"].socket.handle_close()

def save(data):
	pass
