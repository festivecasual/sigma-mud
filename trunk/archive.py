import pickle
import os.path

from common import *


def initialize():
    if not os.path.exists(options["players_db"]):
        player_db = {}
        player_file = open(options["players_db"], "wb")
        pickle.dump(player_db, player_file)
        player_file.close()


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
    stance_list=[]
    default_stance_list={}
    for s in player.stances:
        stance_list.append(s.name)
    for val in weapon_match_val:
        if player.default_stance.has_key(val):
            default_stance_list[val]=player.default_stance[val].name
    
    player_file = open(options["players_db"], "rb")
    player_db = pickle.load(player_file)
    player_file.close()

    player_db[player.name] = pickle.dumps((
        player.password, player.contents,player.worn_items,
        player.equipped_weapon,player.stats,player.points_to_allocate,
        player.gender, player.race,player.HP,stance_list,default_stance_list,player.active_stance.name))
    log("SAVE", "User <%s> saved successfully at %s" % (
			player.name, time_string()), True)

    player_file = open(options["players_db"], "wb")
    pickle.dump(player_db, player_file)
    player_file.close()
