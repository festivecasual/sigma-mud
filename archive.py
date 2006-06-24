import pickle, bsddb

def player_load(name):
	player_db = bsddb.hashopen("data/players.db")
	
	player_db.close()


def player_save(target):
	player_db = bsddb.hashopen("data/players.db")
	
	player_db.close()
