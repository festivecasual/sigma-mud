import traceback
import sys
import command
import time
import random
import os.path
import copy
from string import Template

import task
from entities import Player
from common import *


def handler(val=INFINITE):
    import handler as _handler
    def handler_dec(f):
        f.priority = val
        _handler.functions[f.__name__] = f
        return f
    return handler_dec


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
    return type(object) == Player


def noop(): pass


class InsertedTask(object):
    def __init__(self):
        self.task_init = noop
        self.task_execute = noop
        self.task_deinit = noop


class Duration(object):
    def __init__(self):
        self.start_time=time.time()
        self.duration_in_secs=0
        self.infinite=False
    def remaining_time(self):
        if self.duration_in_secs==INFINITE:
            return INFINITE
        else:
            return max(self.duration_in_secs - int((time.time()-self.start_time)),0)

    def duration_expired(self):
        return (self.remaining_time()==0 and not self.infinite)


class Wait(Duration):
    def __init__(self, p,d):
        duration.__init__(self)
        self.duration_in_secs=d
        self.priority=p


class Offer(object):
    def __init__(self, transfer_item, from_character, to_character):
        self.transfer_item, self.from_character, self.to_character = transfer_item, from_character, to_character

    def warning(self):
        if self not in self.to_character.offers:
            return

        if not self.check_valid():
            self.dequeue()
            return

        self.to_character.send_line(
                'You have yet to accept or refuse the offer of %s by %s.' % (
                        self.transfer_item.name,
                        self.from_character.name,
                        )
                )

        insert_task(self.to_character.name + '_transfer_dequeue', self.dequeue, 30, 1)

    def dequeue(self):
        if self not in self.to_character.offers:
            return

        self.to_character.offers.remove(self)
        self.to_character.send_line('The offer of %s from %s can no longer be accepted.' % (
                self.transfer_item.name,
                self.from_character.name,
                ))
        self.from_character.send_line('Your offer of %s to %s has been abandoned.' % (
                self.transfer_item.name,
                self.to_character.name,
                ))

    def check_valid(self):
        if self.to_character.location != self.from_character.location:
            return False

        if self.transfer_item not in self.from_character.contents:
            return False

        return True


def insert_task(name, task_function, interval, ttl = -1):
    # Construct a dummy "module" for the task
    task_module = InsertedTask()
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


def val2txt(value, value_tuple, txt_tuple):
    for i in range(len(value_tuple)):
        if value_tuple[i]  == value:
            return txt_tuple[i]
    return ''


def txt2val(text, txt_tuple, value_tuple):
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
            if not room.is_door_closed(i):
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
    tx = Offer(item, from_character, to_character)
    to_character.offers.append(tx)
    insert_task(to_character.name + '_transfer_warning', tx.warning, 30, 1)


def transfer_item(item, from_collection, to_collection,amount=None, individual=False):
    if item not in from_collection:
        return False

    if not item.stackable:
            to_collection.append(item)
            from_collection.remove(item)
            return True

    else:
        amount = item.quantity if not amount else amount
        if not individual:
            for t in to_collection:
                if t.name == item.name and t.stackable:     #TODO: NEED TO CHECK FOR ALL UNIQUE IDENTIFIERS! For now, Name is sufficient
                    if t.quantity+amount <= t.max_quantity:
                        t.quantity+=amount
                        item.quantity-=amount
                        if item.quantity == 0:
                            from_collection.remove(item)
                        return True
                    else:
                        o_amount=amount
                        t.quantity=int(t.max_quantity)
                        while amount > t.max_quantity:
                            amount-=t.max_quantity
                            new_item = copy.copy(item)
                            new_item.quantity=amount
                            to_collection.append(new_item)

                        item.quantity-=o_amount
                        if item.quantity == 0:
                            from_collection.remove(item)

                        return True
        new_item=copy.copy(item)
        new_item.quantity=amount
        item.quantity-=amount
        if item.quantity == 0:
            from_collection.remove(item)

        to_collection.append(new_item)


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
        if worn_item.wearable.worn_position == worn_spot:
            count+=1
    return count >= worn_limits[worn_spot]


def add_points(character,number):
    character.points_to_allocate = character.points_to_allocate + number
    return True


def remove_points(character,number):
    character.points_to_allocate = character.points_to_allocate - number
    if character.points_to_allocate < 0:
        character.points_to_allocate = 0
    return True


def raise_stat(character, stat, number):
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


def report(recipients, template, actor, verbs=None, direct=None, indirect=None):
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
    def __init__(self, args, args_consumed=1, matches=[]):
        self.arglist = args[args_consumed:]
        self.matchlist = matches

    def __getitem__(self, key):
        return self.matchlist[key]

    def Complete(self):
        return not self.Remaining()

    def Match(self):
        return len(self.matchlist) > 0 and self.matchlist[-1]

    def Remaining(self):
        return len(self.arglist)

    def CompleteMatch(self):
        if self.Complete() and self.Match():
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

    def Keyword(self, keyword):
        if not self.arglist:
            return Sentence([], 0, self.matchlist + [False])
        if keyword.startswith(self.arglist[0]):
            return Sentence(self.arglist, 1, self.matchlist + [keyword])
        return Sentence([], 0, self.matchlist + [False])

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

    def Literal(self):
        if not self.arglist:
            return Sentence([], 0, self.matchlist + [False])
        return Sentence(self.arglist, 1, self.matchlist + [self.arglist[0]])

    def LiteralBlob(self):
        if not self.arglist:
            return Sentence([], 0, self.matchlist + [False])

        return Sentence([], 0, self.matchlist + [' '.join(self.arglist)])
