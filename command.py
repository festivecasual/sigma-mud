import archive, sha, pickle
from common import *

command_queue = []

def accept_command(speaker, message):
	command_queue.append((speaker, message))

def process_commands():
	while len(command_queue) > 0:
		speaker, message = command_queue.pop(0)

		if speaker.state == STATE_NAME:
			name = message.strip()
			player_file = archive.player_load(name)
			if player_file:
				speaker.name = name
				speaker.proto = player_file
				speaker.state = STATE_PASSWORD
			else:
				speaker.send_line("I do not know that name.")
				speaker.send_line()

		elif speaker.state == STATE_PASSWORD:
			crypter = sha.new()
			crypter.update(message)
			password = crypter.digest()

			if password == speaker.proto[0]:
				log("LOGIN", "User <" + speaker.name + "> logged in at " + time_string())
				speaker.state = STATE_PLAYING
			else:
				speaker.send_line("NO!")
				speaker.send_line()
				speaker.state = STATE_NAME

			speaker.proto = None

		speaker.send_prompt()
