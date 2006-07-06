from common import *

def register_handlers():
	return	{
		 "say" : say,
		 "emote" : emote
		}

def say(data):
	log("EVENT", "say()")

def emote(data):
	log("EVENT", "emote()")
