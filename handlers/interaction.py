from common import *

def register_handlers():
	return	{
		 "say" : say
		}

def say():
	log("EVENT", "say()")
