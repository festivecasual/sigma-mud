import pickle
from common import *


def player_load(name):
	player_file = open(options["players_db"], "rb")
	player_db = pickle.load(player_file)
	player_file.close()

	if player_db.has_key(name):
		ret = pickle.loads(player_db[name])
	else:
		ret = False

	return ret


def player_save(player):
	player_file = open(options["players_db"], "rb")
	player_db = pickle.load(player_file)
	player_file.close()

	player_db[player.name] = pickle.dumps((player.password, player.contents,player.worn_items, 
										   player.equipped_weapon,player.stats,player.points_to_allocate,
										   player.gender, player.race,player.HP))
	log("SAVE", "User <" + player.name + "> saved successfully at " + time_string(), True)
	
	player_file = open(options["players_db"], "wb")
	pickle.dump(player_db, player_file)
	player_file.close()
