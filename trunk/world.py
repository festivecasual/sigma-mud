import sys
import feats
import libsigma
import feats
from common import *


players = []
rooms = {}
denizens = {}
items = {}
denizens_source = {}
items_source = {}
populators = []
placements = []
calendars = []
doors = []
combats = []


def resolve_links():
    for current in rooms.values():
        for i in range(NUM_DIRS):
            if not current.exits[i]:
                continue

            if rooms.has_key(current.exits[i]):
                current.exits[i] = rooms[current.exits[i]]
            elif rooms.has_key(current.area + ":" + current.exits[i]):
                current.exits[i] = rooms[current.area + ":" + current.exits[i]]
            else:
                log("ERROR", "Unresolved room exit linkage: " + current.exits[i] + " (" + current.location + ")", problem=True)
                current.exits[i] = None


def resolve_populators():
    for current in populators:
        if denizens_source.has_key(current.denizen):
            current.denizen = denizens_source[current.denizen]
        elif denizens_source.has_key(current.area + ":" + current.denizen):
            current.denizen = denizens_source[current.area + ":" + current.denizen]
        else:
            log("ERROR", "Unresolved denizen reference: " + current.denizen, problem=True)

        if rooms.has_key(current.target):
            current.target = rooms[current.target]
        elif rooms.has_key(current.area + ":" + current.target):
            current.target = rooms[current.area + ":" + current.target]
        else:
            log("ERROR", "Unresolved target room reference: " + current.target, problem=True)


def resolve_placements():
    for current in placements:
        if items_source.has_key(current.item):
            current.item = items_source[current.item]
        elif items_source.has_key(current.area + ":" + current.item):
            current.item = items_source[current.area + ":" + current.item]
        else:
            log("ERROR", "Unresolved item reference: " + current.item, problem=True)

        if rooms.has_key(current.target):
            current.target = rooms[current.target]
        elif rooms.has_key(current.area + ":" + current.target):
            current.target = rooms[current.area + ":" + current.target]
        else:
            log("ERROR", "Unresolved target room reference: " + current.target, problem=True)


class populator(object):
    def __init__(self, node, area_name, denizen_id, target):
        self.denizen = denizen_id
        self.target = target
        self.area = area_name
        self.flags = []

        self.instance = None

        for flag in node.findall('flag'):
            self.flags.append(strip_whitespace(flag.text))


class placement(object):
    def __init__(self, node, area_name, item_id, target):
        self.item = item_id
        self.target = target
        self.area = area_name
        self.flags = []

        self.instance = None

        for flag in node.findall('flag'):
            self.flags.append(strip_whitespace(flag.text))


class room(object):
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
        if self.exits[direction]!=None:
            if self.doors[direction]==None:
                return True
            if doors[self.doors[direction]].is_open():
                return True
        return False

    def open_door(self, direction):
        if self.doors[direction]!=None:
            doors[self.doors[direction]].status=DOOR_OPEN

    def close_door(self, direction):
        if self.doors[direction]!=None:
            doors[self.doors[direction]].status=DOOR_CLOSED

    def is_door_closed(self,direction):
        if direction != -1:
            if self.doors[direction]!=None:
                return doors[self.doors[direction]].is_closed()
        return False


class entity(object):
    def __init__(self):
        self.name = ''
        self.contents = []
        self.capacity = 0
        self.location = ''
        self.money = 0

        self._desc = ''
        self._keywords = []
        self._short = ''

    @property
    def desc(self):
        return self._desc

    @property
    def short(self):
        return self._short

    @property
    def keywords(self):
        return self._keywords


class item(entity):
    def __init__(self, node):
        entity.__init__(self)

        self.weapon_type = NOT_A_WEAPON
        self.worn_position = NOT_WORN

        self.name = strip_whitespace(required_child(node, 'name').text)

        self._desc = wordwrap(strip_whitespace(required_child(node, 'desc').text))
        self._short = wordwrap(strip_whitespace(required_child(node, 'short').text))

        keywords = node.find('keywords')
        if keywords != None:
            self._keywords.extend(strip_whitespace(keywords.text).lower().split())

        worn = node.find('worn')
        if worn != None:
            self.worn_position = libsigma.txt2worn(strip_whitespace(worn.text))

        weapon = node.find('weapon')
        if weapon != None:
            weapon_type = required_attribute(weapon, 'type')
            self.weapon_type = libsigma.txt2val(weapon_type, weapon_match_txt, weapon_match_val)


class offer(object):
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

        libsigma.insert_task(self.to_character.name + '_transfer_dequeue', self.dequeue, 30, 1)

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
                self.from_character.name,
                ))

    def check_valid(self):
        if self.to_character.location != self.from_character.location:
            return False

        if self.transfer_item not in self.from_character.contents:
            return False

        return True


class character(entity):
    def __init__(self):
        entity.__init__(self)

        self.gender = GENDER_NEUTRAL
        self.race = RACE_NEUTRAL
        self.level = 0

        self.stats = {}
        for stat in stats:
            self.stats[stat] = DEFAULT_STAT

        self.offers = []

        self.points_to_allocate = 0
        self.equipped_weapon = []
        self.equipped_shield = None
        self.worn_items = []
        self.waits=[]
        self.flags = []

        self.combats = []
        self.engaged = None
        self.active_stance=None
        self.default_stance = {}
        
        self.stances=[]
        for s in feats.default_stances:
            self.add_stance(s)
        
        self.active_stance=self.stances[0]
        
        self._balance=0
        self._HP = 0
        self._XP = 0
        self.hidden=False
        
        self.state = STATE_NULL

    def send_prompt(self): pass

    def send(self, s = ""): pass

    def send_line(self, s = "", breaks = 1): pass

    def send_combat_status(self): pass

    def handle_death(self):
        pass

    def check_level(self):
        pass

    @property
    def preferred_weapon_range(self):
        pwr = MELEE_RANGE
        for w in self.equipped_weapon:
            if preferred_range[w.weapon_type] > pwr:
                pwr = preferred_range[w.weapon_type]
        return pwr

    @property
    def max_HP(self):
        return 4*self.stats["strength"] + 2*self.stats["discipline"]

    def set_HP(self, val):
        self._HP = min(max(0, val), self.max_HP)
        if self._HP == 0:
            self.handle_death()

    HP = property(lambda self: self._HP, set_HP)

    def set_XP(self, val):
        # This allows for passive level-up checking for players
        self._XP = val
        self.check_level()

    XP = property(lambda self: self._XP, set_XP)

    def change_balance(self, val):
        self._balance=min (max(val, MIN_BALANCE), MAX_BALANCE)
        return
    
    balance = property(lambda self: self._balance, change_balance)
    
    def can_equip(self,w_type):
        for s in self.stances:
            if s.weapon_type==w_type: 
                return True
        return False

    def add_stance(self,s):
        for sta in self.stances:
            if sta.name==s.name:
                return False
        if not self.default_stance.has_key(s.weapon_type):
            self.default_stance[s.weapon_type]=s
        self.stances.append(s)
        return True
    
class denizen(character):
    def __init__(self, node):
        character.__init__(self)

        self.state = STATE_PLAYING

        self.name = strip_whitespace(required_child(node, 'name').text)
        self._desc = wordwrap(strip_whitespace(required_child(node, 'desc').text))

        self._short = wordwrap(strip_whitespace(required_child(node, 'short').text))

        keywords = node.find('keywords')
        if keywords != None:
            self._keywords.extend(strip_whitespace(keywords.text).lower().split())

        for flag in node.findall('flag'):
            self.flags.append(strip_whitespace(flag.text))

        stat_info = node.find('stats')
        if stat_info != None:
            try:
                self.level = int(required_attribute(stat_info, 'level'))
            except ValueError:
                log("FATAL", "<stats /> level attribute must be an integer", exit_code=1)

            for stat in stats:
                # Obviously needs sophistication
                self.stats[stat] = self.level * 2

            for forced_stat in stat_info.findall('stat'):
                try:
                    self.stats[required_attribute(forced_stat, 'name')] = int(required_attribute(forced_stat, 'value'))
                except KeyError:
                    log("FATAL", "<stat /> name attribute references an invalid statistic", exit_code=1)
                except ValueError:
                    log("FATAL", "<stat /> value attribute must be an integer", exit_code=1)

        self.HP = self.max_HP


class player(character):
    def __init__(self, s=None):
        character.__init__(self)

        self.proto = None

        self.password = None
        self.socket = None
        self.state = STATE_INIT

        self.socket = s
        if self.socket is not None:
            self.send_prompt()

    @property
    def desc(self):
        return self.name + " is here."

    @property
    def short(self):
        return self.name + " is here."

    @property
    def keywords(self):
        return [self.name.lower()]

    def send_prompt(self):
        self.socket.push(prompts[self.state])

        if (self.state == STATE_INIT):
            self.state = STATE_NAME
            self.send_prompt()

    def send(self, s = ""):
        self.socket.push(s)

    def send_line(self, s = "", breaks = 1):
        self.send(s)
        self.send("\r\n" * breaks)

    def send_combat_status(self):
        self.send_line("[HP: " + str(self.HP) + "/" + str(self.max_HP) + " | Balance: " + balance_name[self.balance] +"]" )

    def handle_death(self):
        pass

    def has_waits(self,prior=HIGHEST_PRIORITY):
        for w in self.waits:
            if (not w.duration_expired()) and w.priority <= prior:
                return w.remaining_time()
        return False
    
    def add_wait(self,p,d):
        self.waits.append(wait(p,d))
        self.send_line("[This action adds a " +str(d)+ " second wait]")
        return
    
class calendar(object):
    def __init__(self, node, cname):
        self.name = cname
        self.daylength = 0  # measured in RL hours
        self.yearlength = 0  # measured in IG Days
        self.days_of_week = []
        self.months = {}
        self.monthlist = []
        self.holidays = {}
        self.watershed_name = ''
        self.watershed_date = ''

        dlength = node.find('IGDayLengthInHours')
        if dlength != None:
            try:
                self.daylength = int(strip_whitespace(dlength.text))
            except ValueError:
                log("FATAL", "IGDayLengthInHours property must be an integer", exit_code=1)

        for month in node.findall('month'):
            month_name = required_attribute(month, 'name')
            month_days = required_attribute(month, 'days')

            try:
                self.months[month_name] = int(month_days)
                self.monthlist.append(month_name)
            except ValueError:
                log("FATAL", "days property must be an integer", exit_code=1)

            if self.months[month_name] < 1:
                log("FATAL", "days must be greater than 0", exit_code=1)

        for day in node.findall('day'):
            self.days_of_week.append(strip_whitespace(day.text))

        holidays = node.findall('holiday')
        if holidays:
            holiday_compliance = True
        for holiday in holidays:
            holiday_name = required_attribute(holiday, 'name')
            holiday_mday = required_attribute(holiday, 'month_day')
            holiday_month = required_attribute(holiday, 'month')

            if self.holidays.has_key(holiday_name):
                log("FATAL", "Duplicate holiday name found.  Holiday names must be unique.", exit_code=1)

            try:
                holiday_mday = int(holiday_mday)
            except ValueError:
                log("FATAL", "month_day property must be an integer", exit_code=1)

            if not self.months.has_key(holiday_month):
                holiday_compliance = False
            elif holiday_mday > self.months[holiday_month] or holiday_mday < 1:
                holiday_compliance = False

            if (holiday_compliance):
                self.holidays[holiday_name] = { holiday_month : holiday_mday }
            else:
                log("ERROR", "Cannot create %s holiday" % holiday_name, problem=True)

        watershed = node.find('WatershedEvent')
        if watershed != None:
            ws_title = required_attribute(watershed, 'title')
            ws_date = required_attribute(watershed, 'date')
            self.watershed_name = ws_title
            self.watershed_date = ws_date + " 00:00:00"

        self.yearlength = reduce(lambda x, y: x + y, self.months.values())

    def get_current_IG_DateTime(self):
        return self.get_IG_DateTime(date_time_string())

    def get_IG_DateTime(self, date_time):
        date_diff=self.get_date_diff(date_time)
        IG_days_diff= self.get_IG_days_diff(date_diff)
        IG_date = self.get_IG_date(IG_days_diff)
        IG_date["day_of_week"] = self.get_day_of_week(IG_days_diff)
        IG_date["hour"]= self.get_IG_time(date_diff["hours"],date_diff["minutes"],date_diff["seconds"])["hours"]
        IG_date["minute"]=self.get_IG_time(date_diff["hours"],date_diff["minutes"],date_diff["seconds"])["minutes"]
        return IG_date

    # returns a RL time breakdown between a given time and the watershed date
    def get_date_diff(self,given_time):
        ret={}

        c_y,c_m,c_d,c_h,c_M,c_s = self.unpackDate(given_time)
        z_y,z_m,z_d,z_h,z_M,z_s = self.unpackDate(self.watershed_date)
        given_date = datetime.datetime(int(c_y),int(c_m),int(c_d),int(c_h),int(c_M),int(c_s))
        zero_date = datetime.datetime(int(z_y),int(z_m),int(z_d),int(z_h),int(z_M),int(z_s))
        diff = given_date - zero_date

        ret["days"] = diff.days
        ret["hours"] = diff.seconds / 3600
        remainder = diff.seconds % 3600
        ret["minutes"] = int(remainder / 60)
        ret["seconds"] = remainder % 60
        return ret

    def get_IG_days_diff(self, date_diff):
        return int((date_diff["days"]*24 + date_diff["hours"]) / self.daylength)

    def get_IG_time(self, hours, mins, seconds):
        ret={}
        remainder = (hours%self.daylength) * 3600 + (mins*60) + seconds
        IGHourlength_in_seconds = self.daylength * 150  # 3600 / 24...

        ret["hours"] = int(remainder/IGHourlength_in_seconds)
        remainder%=IGHourlength_in_seconds
        ret["minutes"]= int(remainder/(IGHourlength_in_seconds/60))
        return ret

    # given a difference in days since watershed, give the day of the week
    def get_day_of_week(self, IG_days_diff):
        IG_day_of_week_index = IG_days_diff % len(self.days_of_week)
        return self.days_of_week[IG_day_of_week_index]

    # returns a dictionary of years, months, days
    def get_IG_date(self, IGdays):
        ret = {}
        ret["year"] = IGdays / self.yearlength
        IGdays_remainder = IGdays % self.yearlength

        for month in self.monthlist:
            if IGdays_remainder > self.months[month]:
                IGdays_remainder -= int(self.months[month])
            else:
                ret["month"] = month
                ret["day"] = IGdays_remainder
                break

        return ret

    # returns list in format [month, day, year, hours, mins, seconds]
    def unpackDate(self, date):
        t_date = date.replace(" ", "/")
        t_date = t_date.replace(":", "/")
        sp = t_date.split("/")
        for x in sp:
            x = int(x)
        return sp;


class door(object):
    def __init__(self, node, area_name, index):
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

            if not rooms.has_key(room_id):
                log("FATAL", "Invalid room value in door tag", exit_code=1)
            elif rooms[room_id].exits[libsigma.txt2dir(exit_dir)] == None:
                log("FATAL", "Invalid dir value in door tag", exit_code=1)

            rooms[room_id].doors[libsigma.txt2dir(exit_dir)] = index

    def is_open(self):
        return self.status == DOOR_OPEN

    def is_closed(self):
        return self.status == DOOR_CLOSED or self.is_locked()

    def is_locked(self):
        return self.status == DOOR_LOCKED


# Stores an instance of combat and its attributes
class combat(object):
    def __init__(self, combatant1, combatant2):
        # combatant1 is assumed the aggressor. He is assumed to be
        # engaged initially in this combat, as s/he instigated it
        self.combatant1 = combatant1
        self.combatant2 = combatant2

        self.combatant1_action = None  # may not be used, putting in for now...
        self.combatant2_action = None

        self.strike_queue = []

        self.combat_state = COMBAT_STATE_INITIALIZING
        self.range = NOT_IN_COMBAT

    def release(self):
        combats.remove(self)
        self.combatant1.combats.remove(self)
        self.combatant2.combats.remove(self)
        if self.combatant1.engaged==self:
            self.combatant1.engaged=None
        if self.combatant2.engaged==self:
            self.combatant2.engaged=None

    def queue_strikes(self):
        # section needs work. Defaults to attack, need to do more checks
        self.combatant1_action=COMBAT_ACTION_ATTACKING
        self.combatant2_action=COMBAT_ACTION_ATTACKING
        agil_diff=self.combatant1.stats["agility"] - self.combatant2.stats["agility"]
        percent_success=min(max(agil_diff*5 + 50, 20), 80)
        roll_for_first_strike=libsigma.d100()
        if roll_for_first_strike <= percent_success:
            self.strike_queue.append((self.combatant1, self.combatant2))
            self.strike_queue.append((self.combatant2, self.combatant1))
        else:
            self.strike_queue.append((self.combatant2, self.combatant1))
            self.strike_queue.append((self.combatant1, self.combatant2))
        # end section

class duration(object):
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
    
class wait(duration):
    def __init__(self, p,d):
        duration.__init__(self)
        self.duration_in_secs=d
        self.priority=p
    