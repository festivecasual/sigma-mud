## @package archive
#  Provide functions for manipulating player data in the save database.

import pickle
from common import *

## Retrive player archive structure from the player save database.
#
#  @param name Player name to attempt loading.
def player_load(name):
	player_file = open(options["players_db"], "rb")
	player_db = pickle.load(player_file)
	player_file.close()

	if player_db.has_key(name):
		ret = pickle.loads(player_db[name])
	else:
		ret = False

	return ret

## Generate player archive structure and serialize to the database.
#
#  @param player The player object to serialize.
def player_save(player):
	player_file = open(options["players_db"], "rb")
	player_db = pickle.load(player_file)
	player_file.close()

	player_db[player.name] = pickle.dumps((player.password, player.contents,player.worn_items, player.gender,player.race))
	log("SAVE", "User <" + player.name + "> saved successfully at " + time_string(), True)
	
	player_file = open(options["players_db"], "wb")
	pickle.dump(player_db, player_file)
	player_file.close()
