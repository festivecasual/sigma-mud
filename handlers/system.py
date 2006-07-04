from common import *

def register_handlers():
	return	{
		 "quit" : quit,
		 "save" : save
		}

def quit():
	log("EVENT", "quit()")

def save():
	log("EVENT", "save()")
