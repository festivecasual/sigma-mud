import traceback
import sys
import command
import time
import math
import random
import os.path
from string import Template

import task
import world
import handler as _handler
from common import *


def handler(f):
    _handler.functions[f.__name__] = f
    return f


def safe_mode(function, *args):
    ret = False

    if options['debug'] == 'yes':
        return function(*args)

    try:
        ret = function(*args)
    except Exception as e:
        tb = sys.exc_info()[2]
        last = traceback.extract_tb(tb)[-1]
        log("ERROR", "%s:%d  %s" % (os.path.basename(last[0]), last[1], e), problem=True)

    return ret


def alert(text):
    log("ALERT", text)


def is_player(object):
    return hasattr(object, "socket")


def noop(): pass


class inserted_task(object):
    def __init__(self):
        self.task_init = noop
        self.task_execute = noop
        self.task_deinit = noop


def insert_task(name, task_function, interval, ttl = -1):
    # Construct a dummy "module" for the task
    task_module = inserted_task()
    task_module.task_execute = task_function
    task.tasks[name + '_' + str(time.time())] = (task_module, time.time(), interval, ttl)


def txt2dir(text):
    for i in range(len(dir_match_dir)):
        if dir_match_txt[i].startswith(text):
            return dir_match_dir[i]

    return -1


def dir2txt(dir):
    for i in range(len(dir_match_dir)):
        if dir_match_dir[i] == dir:
            return dir_match_txt[i]
    return ''


def txt2worn(text):
    for i in range(len(worn_match_val)):
        if worn_match_txt[i].startswith(text):
            return worn_match_val[i]

    return -1


def worn2txt(worn):
    for i in range(len(worn_match_val)):
        if worn_match_val[i] == worn:
            return worn_match_txt[i]

    return ''


def val2txt(value, value_tuple,txt_tuple):
    for i in range(len(value_tuple)):
        if value_tuple[i]  == value:
            return txt_tuple[i]
    return ''


def txt2val(text, txt_tuple,value_tuple):
    for i in range(len(value_tuple)):
        if txt_tuple[i].startswith(text):
            return value_tuple[i]

    return -1


def exits(room):
    result = []

    for i in range(len(room.exits)):
        if room.exits[i]:
            result.append(i)

    return result


def open_exits(room):
    result = []

    for i in range(len(room.exits)):
        if room.exits[i]:
            if(not room.is_door_closed(i)):
                result.append(i)
    return result


def enter_room(character, room):
    if character.location:
        character.location.characters.remove(character)
    room.characters.append(character)
    character.location = room


def character_in_room(name, room, self_character = None):
    for search in room.characters:
        for keyword in search.keywords:
            if keyword.startswith(name) and not search.hidden:
                return search
    if "self".startswith(name):
        return self_character
    return None


def item_in_room(name, room):
    for search in room.contents:
        for keyword in search.keywords:
            if keyword.startswith(name):
                return search

    return None


item_in_inventory = item_in_room


def focus_in_room(name, room):
    for key, text in room.foci.items():
        if key.startswith(name):
            return text

    return None


def offer_item(item, from_character, to_character):
    tx = world.offer(item, from_character, to_character)
    to_character.offers.append(tx)
    insert_task(to_character.name + '_transfer_warning', tx.warning, 30, 1)


def transfer_item(item, from_collection, to_collection):
    if item in from_collection:
        to_collection.append(item)
        from_collection.remove(item)
        return True
    else:
        return False


def transfer_money(amount, origin, destination):
    to_transfer = min(origin.money, amount)
    origin.money -= to_transfer
    destination.money += to_transfer


def queue_command(character, text):
    command.accept_command(character, text)


def run_command(character, text):
    if not command.run_command(character, text):
        log("ERROR", "Command <" + text + "> unsuccessful", problem=True)


def at_capacity(character,worn_spot):
    count=0
    for worn_item in character.worn_items:
        if worn_item.worn_position == worn_spot:
            count+=1
    return count >= worn_limit[worn_spot]


def add_points(character,number):
    character.points_to_allocate = character.points_to_allocate + number
    return True


def remove_points(character,number):
    character.points_to_allocate = character.points_to_allocate - number
    if character.points_to_allocate < 0:
        character.points_to_allocate = 0
    return True


def raise_stat(character,stat, number):
    character.stats[stat] = character.stats[stat] + number
    return True


# Report function recipient: the acting player.
SELF =  1
# Report function recipient: the acting player's room.
ROOM =  2
# Report function recipient: the acting player's nearby rooms.
NEAR =  4 # TODO
# Report function recipient: the acting player's area (excluding nearby rooms).
AREA =  8 # TODO
# Report function recipient: the entire game (excluding the active area).
GAME = 16 # TODO


def report(recipients, template, actor, verbs = None, direct = None, indirect = None):
    out = ""
    s = Template(template)

    mapping = {
            "actor" : actor.name
            }
    self_mapping = {
            "actor" : "you"
            }

    if verbs:
        mapping["verb"] = verbs[1]
        self_mapping["verb"] = verbs[0]

    if direct:
        if direct != actor:
            mapping["direct"] = direct.name
            self_mapping["direct"] = direct.name
        else:
            mapping["direct"] = pronoun_reflexive[direct.gender]
            self_mapping["direct"] = "yourself"

    if indirect:
        if indirect != actor:
            mapping["indirect"] = indirect.name
            self_mapping["indirect"] = indirect.name
        else:
            mapping["indirect"] = "itself"
            self_mapping["indirect"] = "yourself"

    if SELF & recipients:
        out = s.safe_substitute(self_mapping)
        out = out[0].upper() + out[1:]
        actor.send_line()
        actor.send_line(out)

    out = s.safe_substitute(mapping)
    out = out[0].upper() + out[1:]

    if ROOM & recipients:
        for search in actor.location.characters:
            if search != actor:
                search.send_line()
                if search == direct:
                    out_special = s.safe_substitute(mapping, direct = "you")
                    out_special = out_special[0].upper() + out_special[1:]
                    search.send_line(out_special)
                elif search == indirect:
                    out_special = s.safe_substitute(mapping, indirect = "you")
                    out_special = out_special[0].upper() + out_special[1:]
                    search.send_line(out_special)
                else:
                    search.send_line(out)
    if NEAR & recipients:
        announce(NEAR, actor.location, out)

    return out


# room based report. Does not originate at a person, rather at a room.
# Since the room is the target, this is the messaging that is used
# only when the message is uniformly presented to all in the room
# with this implementation
def announce(recipients,room, message):

    if(ROOM & recipients):
        for all in room.characters:
            all.send_line(message)
    if(NEAR & recipients):
        for exit in room.exits:         #assuming that NEAR does not require open doors. Good assumption?
            if exit != None:
                announce(ROOM, exit, message)
    #if(AREA & recipients):

    #if(GAME & recipients):
    return


def d100():
    return random.randint(1,100)

def roll_for_success(score_1,score_2, minimum_success, maximum_success, delta_multiplier,skew):
    return d100() < min(max((score_1-score_2) * delta_multiplier + skew, minimum_success), maximum_success)

class Sentence(object):
    def __init__(self, args, args_consumed = 1, matches = []):
        self.arglist = args[args_consumed:]
        self.matchlist = matches

    def __getitem__(self, key):
        return self.matchlist[key]

    def CompleteMatch(self):
        if len(self.arglist) == 0 and len(self.matchlist) > 0 and self.matchlist[-1]:
            return True
        else:
            return False

    def MatchCount(self):
        return len(self.matchlist)

    def Allow(self, token):
        if not self.arglist:
            return Sentence([], 0, self.matchlist)

        if self.arglist[0] == token:
            return Sentence(self.arglist, 1, self.matchlist)
        else:
            return Sentence(self.arglist, 0, self.matchlist)

    def CharacterInRoom(self, room, self_character=None):
        if not self.arglist:
            return Sentence([], 0, self.matchlist + [False])

        result = character_in_room(self.arglist[0], room, self_character)
        if result:
            return Sentence(self.arglist, 1, self.matchlist + [result])

        return Sentence([], 0, self.matchlist + [False])

    def ItemInRoom(self, room):
        if not self.arglist:
            return Sentence([], 0, self.matchlist + [False])

        result = item_in_room(self.arglist[0], room)
        if result:
            return Sentence(self.arglist, 1, self.matchlist + [result])

        return Sentence([], 0, self.matchlist + [False])

    def ItemInInventory(self, character):
        if not self.arglist:
            return Sentence([], 0, self.matchlist + [False])

        result = item_in_inventory(self.arglist[0], character)
        if result:
            return Sentence(self.arglist, 1, self.matchlist + [result])

        return Sentence([], 0, self.matchlist + [False])

    def LiteralBlob(self):
        if not self.arglist:
            return Sentence([], 0, self.matchlist + [False])

        return Sentence([], 0, self.matchlist + [' '.join(self.arglist)])
