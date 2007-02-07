import pickle, bsddb
from sys import argv, exit
import world, importer, handler
from common import *

options["verbose"] = "no"

log("SCRIPT", "Booting core server functionality")
handler.load_handlers()
importer.process_xml()
log("SCRIPT", "Finished loading core functionality")

print

if len(argv) == 4:
	if argv[1] == "update_player" or argv[1] == "add_player":
		try:
			player_db = bsddb.hashopen(options["players_db"])
		except:
			log("FAILURE", "Unable to open the player database")
			exit(1)
			
		player_db[argv[2]] = pickle.dumps((encrypt_password(argv[3]), []))
		player_db.close()
		
		log("SUCCESS", "Player created successfully")
		exit(0)

if len(argv) == 3:
	if argv[1] == "delete_player":
		try:
			player_db = bsddb.hashopen(options["players_db"])
		except:
			log("FAILURE", "Unable to open the player database")
			exit(1)

		try:
			del player_db[argv[2]]
		except:
			log("FAILURE", "Unable to delete player from database")
			exit(1)

		player_db.close()
		
		log("SUCCESS", "Player <" + argv[2] + "> deleted successfully")
		exit(0)

print
print
print "Usage: " + argv[0] + " action [args]"
print
print "Available actions:"
print "  add_player username password"
print "  update_player username password"
print "  delete_player username"