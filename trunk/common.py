import time
import hashlib
import os.path
import string
import sys


def log(label, text, trivial=False, problem=False, exit_code=None):
    if options["verbose"] == "silent":
        if problem or exit_code:
            print text
    elif not (trivial and (options["verbose"] == "no")):
        if exit_code or problem:
            label = '-  ' + label
        print "%-10s | %s" % (label, text)
    if exit_code != None:
        sys.exit(exit_code)


def time_string():
    return time.strftime("%H:%M:%S")


def date_time_string():
    return time.strftime("%Y/%m/%d %H:%M:%S")


def encrypt_password(password):
    return hashlib.sha1(password).digest()


def strip_whitespace(text):
    return ' '.join(text.split())


def wordwrap(text, width = -1):
    working = text
    wrapped = ""

    if width == -1:
        width = int(options["wrap_size"])

    while len(working) > width:
        pos = working.rfind(" ", 0, width)

        if pos > -1:
            wrapped += working[:pos] + "\r\n"
            working = working[pos:].lstrip()
        else:
            wrapped += working[:(width - 1)] + "-\r\n"
            working = working[(width - 1):]

    return wrapped + working


def ordinals(int_val):
    if(int(int_val)%10==1 and int(int_val)%100!=11):
        return str(int_val) + "st"
    elif(int(int_val)%10==2 and int(int_val)%100!=12):
        return str(int_val) + "nd"
    elif(int(int_val)%10==3 and int(int_val)%100!=13):
        return str(int_val) + "rd"
    return str(int_val) + "th"


def sigma_path():
    sigma_command = os.path.dirname(sys.argv[0])
    return os.path.abspath(sigma_command)


def required_attribute(element, attribute, cast=None):
    content = element.get(attribute, False) or log(
        "FATAL",
        "<%s> element requires attribute '%s'" % (element.tag, attribute),
        exit_code=1)
    if cast:
        try:
            return cast(content)
        except ValueError:
            log("FATAL", "%s attribute in <%s> expects type '%s'" % (attribute, element.tag, cast.__name__), exit_code=1)
    return content


def required_child(element, tag):
    match = element.find(tag)
    if match != None:
        return match
    else:
        log("FATAL", "<%s> element requires child node '%s'" % \
            (element.tag, tag), exit_code=1)


def singleton(cls):
    instance_container = []
    def getinstance():
        if not len(instance_container):
            instance_container.append(cls())
        return instance_container[0]
    return getinstance


whitespace = ["\t", "\n", "\f", "\r", "\v", "  "]
password_characters = string.letters + string.digits + '!@#$%^&*()-_=+[]\{}|;:?/.,<>~'


def valid_name(name):
    if len(name) < 3:
        return False
    elif name[0] not in string.uppercase:
        return False
    elif name != filter(lambda c: c in string.letters, name):
        return False
    else:
        return True


def valid_password(password):
    if len(password) < 5:
        return False
    elif password != filter(lambda c: c in password_characters, password):
        return False
    else:
        return True


# Connection states
STATE_NULL = 0
STATE_INIT = 1
STATE_NAME = 2
STATE_PASSWORD = 3
STATE_CONFIG_NAME = 4
STATE_CONFIG_PASSWORD = 5
STATE_CONFIG_CHAR = 6
STATE_CONFIG_STATS = 7
STATE_PLAYING = 8


# Combat states
COMBAT_STATE_INITIALIZING = 1
COMBAT_STATE_ENGAGING = 2
COMBAT_STATE_FIGHTING = 3
COMBAT_STATE_INTERMISSION = 4


# Combat actions
COMBAT_ACTION_ATTACKING = 1
COMBAT_ACTION_ADVANCING = 2
COMBAT_ACTION_WITHDRAWING = 3
COMBAT_ACTION_IDLE = 4
COMBAT_ACTION_RETREATING = 5


# Denizen corpse item reference
CORPSE_REFERENCE='system:corpse'


# Infinity Value
INFINITE = -999

# Operators
bonus_operators = ('*','+')


# Directions
DIR_NORTH = 0
DIR_NORTHEAST = 1
DIR_EAST = 2
DIR_SOUTHEAST = 3
DIR_SOUTH = 4
DIR_SOUTHWEST = 5
DIR_WEST = 6
DIR_NORTHWEST = 7
DIR_UP = 8
DIR_DOWN = 9
DIR_ENTER = 10
DIR_LEAVE = 11


# Total number of directions
NUM_DIRS = 12


# Tuple for matching direction text
dir_match_txt = (
    "north",
    "northeast",
    "northwest",
    "ne",
    "nw",
    "east",
    "south",
    "southeast",
    "southwest",
    "se",
    "sw",
    "west",
    "up",
    "down",
    "enter",
    "leave",
    )


# Tuple for matching direction constants
dir_match_dir = (
    DIR_NORTH,
    DIR_NORTHEAST,
    DIR_NORTHWEST,
    DIR_NORTHEAST,
    DIR_NORTHWEST,
    DIR_EAST,
    DIR_SOUTH,
    DIR_SOUTHEAST,
    DIR_SOUTHWEST,
    DIR_SOUTHEAST,
    DIR_SOUTHWEST,
    DIR_WEST,
    DIR_UP,
    DIR_DOWN,
    DIR_ENTER,
    DIR_LEAVE,
    )


# States for doors
DOOR_OPEN = 0
DOOR_CLOSED = 1
DOOR_LOCKED = 2

conditions=("auto","activate")

# context and descriptions

ALL_CONTEXT="all"

contexts={
    "all": "in all cases",
    "combat": "for all combat actions" ,     
    "dodging": "when dodging",      
    "retreating": "when attempting to retreat"      
          
          
    }


# Weapons
weapon_types=("sword","mace","bow","crossbow","knife","spear","staff","greatsword","mallet","bare handed")
#TODO: Projectiles (light, heavy)

# Worn items
worn_limits={
        "head": 1,
        "neck": 1,
        "torso": 1,
        "arms": 2,
        "wrists": 2,
        "fingers": 10,
        "legs": 1,
        "feet": 1,
        "waist": 1,
        "back": 1,  # Cloaks/Robes
        "shoulder": 2,
        "hands": 1,
        }
worn_positions=worn_limits.keys()

# Ammunition
ammo_requirements={
        "bow":"arrow",
        "crossbow":"quarrel",
        }
ammo_weapons=ammo_requirements.keys()
ammo_types=ammo_requirements.values()


# Combat ranges: difference between the integers is significant (represents distance)
NOT_IN_COMBAT=0
MELEE_RANGE=1
SWORD_RANGE=2
POLE_RANGE=4
BOW_RANGE=6

range_match_txt=("melee","sword","pole","bow")
range_match_val=(MELEE_RANGE,SWORD_RANGE,POLE_RANGE,BOW_RANGE)


# Damage multipliers at differing ranges
weapon_range={}
weapon_range['sword']={SWORD_RANGE:1.0,MELEE_RANGE:.75,POLE_RANGE:.25}
weapon_range['mace']={SWORD_RANGE:1.0,MELEE_RANGE:.60}
weapon_range['bow']={BOW_RANGE:1.0,POLE_RANGE:.90}
weapon_range['crossbow']={BOW_RANGE:1.0,POLE_RANGE:.80,SWORD_RANGE:.60}
weapon_range['knife']={MELEE_RANGE:1.0,SWORD_RANGE:.90}
weapon_range['spear']={POLE_RANGE:1.0,SWORD_RANGE:.70}
weapon_range['staff']={POLE_RANGE:1.0,SWORD_RANGE:.95}
weapon_range['greatsword']={SWORD_RANGE:1.0,MELEE_RANGE:.30,POLE_RANGE:.80}
weapon_range['mallet']={SWORD_RANGE:1.0,POLE_RANGE:1.0}
weapon_range['bare handed']={MELEE_RANGE:1.0,SWORD_RANGE:.75}


# General damage multiplier for each weapon type
weapon_damage_multiplier={}
weapon_damage_multiplier['sword']=1.0
weapon_damage_multiplier['mace']=1.2
weapon_damage_multiplier['bow']=.8
weapon_damage_multiplier['crossbow']=.4
weapon_damage_multiplier['knife']=.8
weapon_damage_multiplier['spear']=.9
weapon_damage_multiplier['staff']=.5
weapon_damage_multiplier['greatsword']=1.4
weapon_damage_multiplier['mallet']=1.88
weapon_damage_multiplier['bare handed']=.75


# Range for weapon types
preferred_range={}
preferred_range['sword']=SWORD_RANGE
preferred_range['mace']=SWORD_RANGE
preferred_range['bow']=BOW_RANGE
preferred_range['crossbow']=BOW_RANGE
preferred_range['knife']=MELEE_RANGE
preferred_range['spear']=POLE_RANGE
preferred_range['staff']=POLE_RANGE
preferred_range['greatsword']=SWORD_RANGE
preferred_range['mallet']=POLE_RANGE
preferred_range['bare handed']=MELEE_RANGE


# Damage types
damage_types = ("impact","puncture","slash","burn","cold","electric","divine","profane")


# Stats
DEFAULT_STAT=-1
stats=("strength","intelligence","discipline","agility","charisma","perception")


# Gender handling
GENDER_NEUTRAL='Neutral'
genders=(GENDER_NEUTRAL,'Male','Female')
pronoun_reflexive=dict(zip(genders, ('itself','himself','herself')))
pronoun_subject=dict(zip(genders, ('it','he','she')))
pronoun_object=dict(zip(genders, ('it','him','her')))
pronoun_possessive=dict(zip(genders, ('its','his','her')))


# Race handling
RACE_NEUTRAL = "None"
races=(RACE_NEUTRAL,'Human','Elf','Dwarf','Orc','Wyvernfolk')


# Priorities
HIGHEST_PRIORITY=0
WALKING_PRIORITY=4


# Balance ranges
MIN_BALANCE=-11
MAX_BALANCE=11


# Balance messaging
balance_name={}
balance_name[-11] = "Completely Unbalanced"
balance_name[-10] = "Wildly unbalanced (-)"
balance_name[-9]  = "Wildly unbalanced"
balance_name[-8]  = "Wildly unbalanced (+)"
balance_name[-7]  = "Unbalanced (-)"
balance_name[-6]  = "Unbalanced"
balance_name[-5]  = "Unbalanced (+)"
balance_name[-4]  = "Slightly unbalanced (-)"
balance_name[-3]  = "Slightly unbalanced"
balance_name[-2]  = "Slightly unbalanced (+)"
balance_name[-1]  = "Neutrally balanced (-)"
balance_name[0]   = "Neutrally balanced"
balance_name[1]   = "Neutrally balanced (+)"
balance_name[2]   = "Better balanced (-)"
balance_name[3]   = "Better balanced"
balance_name[4]   = "Better balanced (+)"
balance_name[5]   = "Well balanced (-)"
balance_name[6]   = "Well balanced"
balance_name[7]   = "Well balanced (+)"
balance_name[8]   = "Superbly balanced (-)"
balance_name[9]   = "Superbly balanced"
balance_name[10]  = "Superbly balanced (+)"
balance_name[11]  = "Indelibly balanced"


# Balance multipliers
balance_multiplier={}
balance_multiplier[-11] = 0.5
balance_multiplier[-10] = 0.7
balance_multiplier[-9]  = 0.7
balance_multiplier[-8]  = 0.7
balance_multiplier[-7]  = 0.8
balance_multiplier[-6]  = 0.8
balance_multiplier[-5]  = 0.8
balance_multiplier[-4]  = 0.9
balance_multiplier[-3]  = 0.9
balance_multiplier[-2]  = 0.9
balance_multiplier[-1]  = 1.0
balance_multiplier[0]   = 1.0
balance_multiplier[1]   = 1.0
balance_multiplier[2]   = 1.1
balance_multiplier[3]   = 1.1
balance_multiplier[4]   = 1.1
balance_multiplier[5]   = 1.2
balance_multiplier[6]   = 1.2
balance_multiplier[7]   = 1.2
balance_multiplier[8]   = 1.3
balance_multiplier[9]   = 1.3
balance_multiplier[10]  = 1.3
balance_multiplier[11]  = 1.5


# Prompts (and default values)
prompts = {
    STATE_INIT : "\r\n\r\nWelcome to the Sigma Environment v. 0.0.1!\r\n\r\n",
    STATE_NAME : "Please enter your name:\r\n(type 'new' to create a new character)\r\n ",
    STATE_PASSWORD : "Your password: ",
    STATE_PLAYING : "\r\n> ",
    STATE_CONFIG_NAME : "Please provide what your name will be: ",
    STATE_CONFIG_PASSWORD : "Please provide a password: ",
    STATE_CONFIG_CHAR : "Your choice: ",
    STATE_CONFIG_STATS : "Pick a number: "
    }


# Basic configurable options (and default values)
options = {
    "bind_address" : "",  # "" is a special system identifier for * (all)
    "bind_port" : "4000",  # The server's listening port
    "default_start" : "system:default",  # Default starting room
    "wrap_size" : "60",  # Default word-wrap line length
    "verbose" : "yes",  # Display "trivial" log entries?
    "debug" : "no",  # Halt on errors from safe_mode?
    "root_dir" : sigma_path(),  # Where to look for designer modules and XML files
    "players_db" : os.path.join(sigma_path(), "config", "players.db"),  # Location of player database
    "currency" : 'gold',  # Game currency unit
    }


# Defines system directories for items that are searched dynamically
directories = {
    "xml_root" : os.path.join(options["root_dir"], "config"),  # XML root directory and location of server.xml
    "tasks_root" : os.path.join(options["root_dir"], "tasks"),  # Root directory for task modules
    "handlers_root" : os.path.join(options["root_dir"], "handlers"),  # Root directory for handler modules
    }
