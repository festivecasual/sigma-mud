import pickle, bsddb
from common import *

def player_load(name):
	player_db = bsddb.hashopen("data/players.db")

	if player_db.has_key(name):
		ret = pickle.loads(player_db[name])
	else:
		ret = False

	player_db.close()
	return ret


def player_save(player):
	player_db = bsddb.hashopen("data/players.db")

	player_db[player.name] = pickle.dumps((player.password, player.contents))
	log("SAVE", "User <" + player.name + "> saved successfully at " + time_string(), True)
	
	player_db.close()
