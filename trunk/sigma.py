import asyncore
import sys
import pickle
import archive, command, handler, importer, network, task, world
from common import *


def main():
	log("SYSTEM", "Startup in progress")

	log("MODULES", "Inspecting task modules")
	task.load_tasks()

	log("MODULES", "Inspecting handler modules")
	handler.load_handlers()

	log("XML", "Processing server.xml")
	importer.process_xml()

	log("WORLD", "Resolving location linkages")
	world.resolve_links()
	
	log("WORLD", "Resolving populator objects")
	world.resolve_populators()
	
	log("WORLD", "Resolving placement objects")
	world.resolve_placements()

	log("NETWORK", "Initializing master socket")
	listener = network.server_socket()
	
	log("TASK", "Initializing task modules")
	task.init_tasks()

	log("SYSTEM", "Startup complete, entering main loop")
	while True:
		try:
			asyncore.loop(timeout=0.1, count=1)
			command.process_commands()
			task.run_tasks()
		except KeyboardInterrupt:
			print("")
			log("CONSOLE", "Keyboard interrupt detected")
			break

	log("SYSTEM", "Shutdown in progress")

	log("NETWORK", "Shutting down master socket")
	listener.close()

	log("MODULES", "Deinitializing task modules")
	task.deinit_tasks()

	log("SYSTEM", "Shutdown complete")


def players():
	log("SCRIPT", "Booting core server functionality")
	handler.load_handlers()
	importer.process_xml()
	log("SCRIPT", "Finished loading core functionality")
	log("SCRIPT", "Retreiving player information from database")
	player_file = open(options["players_db"], "rb")
	player_db = pickle.load(player_file)
	player_file.close()
	players = len(player_db)
	log("SCRIPT", "Loaded %s player%s from database" % (players, '' if players == 1 else 's'))
	
	print
	i = 0
	names = player_db.keys()
	names.sort()
	for p in names:
		i = i + 1
		print '%d: %s' % (i, p)
	print
	n = raw_input('Load player index (blank to cancel): ')
	try:
		n = int(n)
		if n < 1 or n > len(names):
			print 'Cancelled.'
			sys.exit(0)
		name = names[n - 1]
		player = archive.player_load(name)
	except (ValueError, IndexError):
		sys.exit(1)
	if not player:
		choice = ''
		raw_input('Player could not be loaded properly.  Delete? (Y/N): ')
		if choice.upper() == 'Y':
			del player_db[name]
		sys.exit(0)
	
	(
		p_password,
		p_contents,
		p_worn,
		p_equipped,
		p_stats,
		p_points,
		p_gender,
		p_race,
		p_HP,
		) = player
	
	print
	print name
	print p_gender, p_race
	for stat, value in p_stats.items():
		print ' %s: %d' % (stat, value)
	print
	action = raw_input('Action ([p]assword, [d]elete), [c]ancel): ')
	if action == '':
		sys.exit(0)
	elif 'password'.startswith(action.lower()):
		p_password = encrypt_password(raw_input('New password: '))
		player = (
			p_password,
			p_contents,
			p_worn,
			p_equipped,
			p_stats,
			p_points,
			p_gender,
			p_race,
			p_HP,
			)
		
		player_db[name] = pickle.dumps(player)
		player_file = open(options["players_db"], "wb")
		pickle.dump(player_db, player_file)
		player_file.close()
		print 'Password written.'
	elif 'delete'.startswith(action.lower()):
		confirm = raw_input('Really delete? (Y/N): ')
		if confirm.upper() == 'Y':
			del player_db[name]
			player_file = open(options["players_db"], "wb")
			pickle.dump(player_db, player_file)
			player_file.close()
			print 'Deletion complete.'
		else:
			print 'Deletion cancelled.'
	else:
		print 'Cancelled.'


if __name__ == "__main__":
	if len(sys.argv) <= 1:
		main()
	elif sys.argv[1] == 'players':
		players()
