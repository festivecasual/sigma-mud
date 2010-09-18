import libsigma
from common import *


@singleton
class World(object):
    def __init__(self):
        self.players = []

        self.rooms = {}
        self.denizens = {}
        self.items = {}

        self.denizens_source = {}
        self.items_source = {}

        self.populators = []
        self.placements = []
        self.calendars = []
        self.doors = []
        self.combats = []

    def resolve_exits(self):
        for r in self.rooms.values():
            for i in range(NUM_DIRS):
                if not r.exits[i]:
                    continue

                if self.rooms.has_key(r.exits[i]):
                    r.exits[i] = self.rooms[r.exits[i]]
                elif self.rooms.has_key(r.area + ":" + r.exits[i]):
                    r.exits[i] = self.rooms[r.area + ":" + r.exits[i]]
                else:
                    log("ERROR", "Unresolved room exit linkage: %s (%s)" % (r.exits[i], r.location), problem=True)
                    r.exits[i] = None

    def resolve_populators(self):
        for p in self.populators:
            if self.denizens_source.has_key(p.denizen):
                p.denizen = self.denizens_source[p.denizen]
            elif self.denizens_source.has_key(p.area + ":" + p.denizen):
                p.denizen = self.denizens_source[p.area + ":" + p.denizen]
            else:
                log("ERROR", "Unresolved denizen reference: " + p.denizen, problem=True)

            if self.rooms.has_key(p.target):
                p.target = self.rooms[p.target]
            elif self.rooms.has_key(p.area + ":" + p.target):
                p.target = self.rooms[p.area + ":" + p.target]
            else:
                log("ERROR", "Unresolved target room reference: " + p.target, problem=True)

    def resolve_placements(self):
        for p in self.placements:
            if self.items_source.has_key(p.item):
                p.item = self.items_source[p.item]
            elif self.items_source.has_key(p.area + ":" + p.item):
                p.item = self.items_source[p.area + ":" + p.item]
            else:
                log("ERROR", "Unresolved item reference: " + p.item, problem=True)

            if self.rooms.has_key(p.target):
                p.target = self.rooms[p.target]
            elif self.rooms.has_key(p.area + ":" + p.target):
                p.target = self.rooms[p.area + ":" + p.target]
            else:
                log("ERROR", "Unresolved target room reference: " + p.target, problem=True)


class Populator(object):
    def __init__(self, node, area_name, denizen_id, target):
        self.denizen = denizen_id
        self.target = target
        self.area = area_name
        self.flags = []

        self.instance = None

        for flag in node.findall('flag'):
            self.flags.append(strip_whitespace(flag.text))


class Placement(object):
    def __init__(self, node, area_name, item_id, target, quantity):
        self.item = item_id
        self.target = target
        self.area = area_name
        self.flags = []
        self.quantity = quantity

        self.instance = None

        for flag in node.findall('flag'):
            self.flags.append(strip_whitespace(flag.text))


class Room(object):
    def __init__(self, ref, node):
        self.location = ref
        self.characters = []
        self.exits = [None] * NUM_DIRS
        self.altmsg = [None] * NUM_DIRS
        self.doors = [None] * NUM_DIRS
        self.foci = {}
        self.contents = []
        self.capacity = 0

        self.name = strip_whitespace(required_child(node, 'name').text)
        self.desc = wordwrap(strip_whitespace(required_child(node, 'desc').text))

        for focus in node.findall('focus'):
            name = required_attribute(focus, 'name')
            description = wordwrap(strip_whitespace(focus.text))
            self.foci[name] = description

        for exit_node in node.findall('exit'):
            exit_dir = required_attribute(exit_node, 'dir')
            exit_target = required_attribute(exit_node, 'target')
            direction = libsigma.txt2dir(exit_dir)
            if direction == -1:
                log('FATAL', "Bad exit direction: '%s'" % exit_dir, exit_code=1)
            self.exits[direction] = exit_target
            altmsg = exit_node.get('altmsg')
            if altmsg:
                self.altmsg[direction] = altmsg

    @property
    def area(self):
        return self.location[:self.location.find(":")]

    def can_character_go(self, direction):
        if self.exits[direction] != None:
            if self.doors[direction] == None:
                return True
            if self.doors[direction].is_open():
                return True
        return False

    def open_door(self, direction):
        if self.doors[direction] != None:
            self.doors[direction].status = DOOR_OPEN

    def close_door(self, direction):
        if self.doors[direction] != None:
            self.doors[direction].status = DOOR_CLOSED

    def is_door_closed(self,direction):
        if direction != -1:
            if self.doors[direction]!=None:
                return self.doors[direction].is_closed()
        return False


class Door(object):
    def __init__(self, node, area_name):
        self.exits = {}
        self.status = DOOR_CLOSED
        self.lockable = False
        self.keys = {}

        for door_exit in node.findall('exit'):
            exit_room = required_attribute(door_exit, 'room')
            exit_dir = required_attribute(door_exit, 'dir')

            if exit_room.find(':') != -1:
                room_id = exit_room
            else:
                room_id = '%s:%s' % (area_name, exit_room)

            w = World()
            if not w.rooms.has_key(room_id):
                log("FATAL", "Invalid room value in door tag", exit_code=1)
            elif w.rooms[room_id].exits[libsigma.txt2dir(exit_dir)] == None:
                log("FATAL", "Invalid dir value in door tag", exit_code=1)
            w.rooms[room_id].doors[libsigma.txt2dir(exit_dir)] = self

    def is_open(self):
        return self.status == DOOR_OPEN

    def is_closed(self):
        return self.status == DOOR_CLOSED or self.is_locked()

    def is_locked(self):
        return self.status == DOOR_LOCKED
