import cPickle as pickle
import os.path

import feats
from common import *


class Archive(object):
    def __init__(self):
        self.path = options["players_db"]
        if not os.path.exists(self.path):
            try:
                with open(self.path, "wb") as player_file:
                    pickle.dump({}, player_file)
            except IOError:
                log("ARCHIVE", "Archive file could not be initialized", problem=True)
                return

    def load(self, name, player):
        try:
            with open(self.path, "rb") as player_file:
                player_db = pickle.load(player_file)
                if player_db.has_key(name):
                    proto = pickle.loads(player_db[name])
                    apply_proto(player, name, proto)
                    return True
                else:
                    return False
        except IOError:
            log("LOAD", "Could not open player database", problem=True)
            return False

    def save(self, player):
        player_db = None
        try:
            with open(self.path, "rb") as player_file:
                player_db = pickle.load(player_file)
        except IOError:
            log("SAVE", "Could not load player database from file", problem=True)
            return False

        stance_list = [s.name for s in player.stances]
        default_stance_list = dict([(id, stance.name) for id, stance in player.default_stance.items()])
        player_db[player.name] = pickle.dumps((
                player.password, player.contents,player.worn_items,
                player.equipped_weapon,player.stats,player.points_to_allocate,
                player.gender, player.race, player.HP, stance_list, default_stance_list, player.active_stance.name
                ))

        try:
            with open(options["players_db"], "wb") as player_file:
                pickle.dump(player_db, player_file)
        except IOError:
            log("SAVE", "Could not write player database to file", problem=True)
            return False

        log("SAVE", "User <%s> saved at %s" % (player.name, time_string()), trivial=True)
        return True

    def find(self, name):
        try:
            with open(self.path, "rb") as player_file:
                player_db = pickle.load(player_file)
                return player_db.has_key(name)
        except IOError:
            log("LOAD", "Could not open player database", problem=True)
            return False

    def list(self):
        try:
            with open(self.path, "rb") as player_file:
                player_db = pickle.load(player_file)
                return player_db
        except IOError:
            log("LOAD", "Could not open player database", problem=True)
            return []

    def delete(self, name):
        player_db = None
        try:
            with open(self.path, "rb") as player_file:
                player_db = pickle.load(player_file)
        except IOError:
            log("SAVE", "Could not load player database from file", problem=True)
            return False

        if player_db.has_key(name):
            del player_db[name]

        try:
            with open(options["players_db"], "wb") as player_file:
                pickle.dump(player_db, player_file)
        except IOError:
            log("SAVE", "Could not write player database to file", problem=True)
            return False


def apply_proto(player, name, proto):
    try:
        player.name = name
        (player.password, player.contents, player.worn_items, player.equipped_weapon,
                player.stats, player.points_to_allocate, player.gender, player.race, player.HP,
                ) = proto[:9]

        for s in proto[9]:
            if feats.stances.has_key(s):
                if not feats.stances[s].default:  # Handled by character class constructor
                    player.stances.append(feats.stances[s])
            else:
                log("WARNING", "Could not load stance %s for <%s>" % (s, player.name), problem=True)

        for val in weapon_types:
            if proto[10].has_key(val):
                player.default_stance[val]=feats.stances[proto[10][val]]

        player.active_stance=feats.stances[proto[11]]

    except IndexError:
        log("WARNING", "Could not load entire player file for <%s>" % player.name, problem=True)
