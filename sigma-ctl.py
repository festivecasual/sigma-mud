import pickle, bsddb
from sys import argv, exit
import world
from common import *

if len(argv) == 4:
	if argv[1] == "update_player" or argv[1] == "add_player":
		player_db = bsddb.hashopen(options["players_db"])
		player_db[argv[2]] = pickle.dumps((encrypt_password(argv[3]), []))
		player_db.close()
		
		log("SUCCESS", "Player created successfully")
		exit(0)
