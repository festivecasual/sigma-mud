from common import *

def register_handlers():
	return	{
		 "quit" : quit,
		 "save" : save
		}

def quit(data):
	log("EVENT", "quit()")

def save(data):
	log("EVENT", "save()")
