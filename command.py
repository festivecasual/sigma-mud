from common import *

command_queue = []

def accept_command(speaker, message):
	command_queue.append((speaker, message))

def process_commands():
	while len(command_queue) > 0:
		command = command_queue.pop(0)

		log("DEBUG", str(command[0]) + ' said, [' + command[1] + ']')
