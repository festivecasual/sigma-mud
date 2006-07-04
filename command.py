import sha, pickle, shlex
import archive, world
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
				speaker.send_line("I do not know that name.", 2)

		elif speaker.state == STATE_PASSWORD:
			password = encrypt_password(message)

			if password == speaker.proto[0]:
				# Do a dupe check to ensure no double logins before entering STATE_PLAYING
				if True in [(check_player.name == speaker.name) for check_player in world.players]:
					speaker.send_line("This name is already active.", 2)
					speaker.name = None
					speaker.proto = None
					speaker.state = STATE_NAME
				else:
					log("LOGIN", "User <" + speaker.name + "> logged in at " + time_string())

					# Copy proto contents to main player class
					speaker.password = speaker.proto[0]
					speaker.contents = speaker.proto[1]

					# Add player to master players list
					world.players.append(speaker)

					speaker.state = STATE_PLAYING
			else:
				speaker.send_line("Incorrect password.", 2)
				speaker.name = None
				speaker.proto = None
				speaker.state = STATE_NAME

		elif speaker.state == STATE_PLAYING:
			tokens = shlex.split(message)

			if len(tokens) and tokens[0] == 'quit':
				import asyncore
				speaker.socket.handle_close()
				continue;

		speaker.send_prompt()
