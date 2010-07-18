import time
import datetime
import hashlib
import os.path
import sys


def log(label, text, trivial=False, problem=False, exit_code=None):
    if not (trivial and (options["verbose"] == "no")):
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
    new = text
    old = ""

    while new != old:
        old = new
        for c in whitespace:
            new = new.replace(c, " ")

    return new.strip()


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


def required_attribute(element, attribute):
    return element.get(attribute, False) or log(
        "FATAL",
        "<%s> element requires attribute '%s'" % (element.tag, attribute),
        exit_code=1)


def required_child(element, tag):
    match = element.find(tag)
    if match != None:
        return match
    else:
        log("FATAL", "<%s> element requires child node '%s'" % \
            (element.tag, tag), exit_code=1)


whitespace = ["\t", "\n", "\f", "\r", "\v", "  "]


# Playing (connection) states
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


#Combat actions
COMBAT_ACTION_ATTACKING = 1
COMBAT_ACTION_ADVANCING = 2
COMBAT_ACTION_WITHDRAWING = 3
COMBAT_ACTION_IDLE = 4


#Infinity Value
INFINITE = -999

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


# Wear places and limit for items of this type to be worn
worn_limit = {}
NOT_WORN = 0

HEAD_WORN = 1
worn_limit[HEAD_WORN] = 1

NECK_WORN = 2
worn_limit[NECK_WORN] = 1

TORSO_WORN = 3
worn_limit[TORSO_WORN] = 1

ARM_WORN = 4
worn_limit[ARM_WORN] = 2

WRIST_WORN = 5
worn_limit[WRIST_WORN] = 2

FINGER_WORN = 6
worn_limit[FINGER_WORN] = 10

LEG_WORN = 7
worn_limit[LEG_WORN] = 1

FOOT_WORN = 8
worn_limit[FOOT_WORN] = 1

WAIST_WORN = 9
worn_limit[WAIST_WORN] = 1

BACK_WORN = 10  # cloaks/robes and such
worn_limit[BACK_WORN] = 1

SHOULDER_WORN =11
worn_limit[SHOULDER_WORN] = 2

HAND_WORN = 12
worn_limit[HAND_WORN] = 1

# Tuple for matching worn constants
worn_match_txt=(
    "not worn","head","neck",
    "torso","arms","wrists",
    "fingers","legs","feet",
    "waist","back","shoulder"
    "hands",
    )

worn_match_val=(
NOT_WORN, HEAD_WORN, NECK_WORN,
TORSO_WORN,ARM_WORN,WRIST_WORN,
FINGER_WORN,LEG_WORN,FOOT_WORN,
WAIST_WORN,BACK_WORN,SHOULDER_WORN
)


# Weapon types
NOT_A_WEAPON=0
SWORD=1
MACE=2
LONGBOW=3
CROSSBOW=4
KNIFE=5
SPEAR=6
STAFF=7
GREATSWORD=8
MALLET=9
BARE_HAND=10

weapon_match_val = (SWORD,MACE,LONGBOW,CROSSBOW,KNIFE,SPEAR,STAFF,GREATSWORD,MALLET, BARE_HAND)
weapon_match_txt = ("sword","mace","longbow","crossbow","knife","spear","staff","greatsword","mallet","bare handed")


#Combat Ranges. Difference between the integers is significant. Represents distance.
NOT_IN_COMBAT=0
MELEE_RANGE=1
SWORD_RANGE=2
POLE_RANGE=4
BOW_RANGE=6

range_match_txt=("melee", "sword","pole","bow")
range_match_val=(MELEE_RANGE,SWORD_RANGE,POLE_RANGE,BOW_RANGE)

#range for weapon types
weapon_range={}
preferred_range={}

#Damage multipliers at differing ranges
weapon_range[BARE_HAND]={MELEE_RANGE:1.0,SWORD_RANGE:.75}
weapon_range[SWORD]={SWORD_RANGE:1.0,MELEE_RANGE:.75,POLE_RANGE:.25}
weapon_range[MACE]={SWORD_RANGE:1.0,MELEE_RANGE:.60}
weapon_range[LONGBOW]={BOW_RANGE:1.0,POLE_RANGE:.90}
weapon_range[CROSSBOW]={BOW_RANGE:1.0,POLE_RANGE:.80,SWORD_RANGE:.60}
weapon_range[KNIFE]={MELEE_RANGE:1.0,SWORD_RANGE:.90}
weapon_range[SPEAR]={POLE_RANGE:1.0,SWORD_RANGE:.70}
weapon_range[STAFF]={POLE_RANGE:1.0,SWORD_RANGE:.95}
weapon_range[GREATSWORD]={SWORD_RANGE:1.0,MELEE_RANGE:.30,POLE_RANGE:.80}
weapon_range[MALLET]={SWORD_RANGE:1.0,POLE_RANGE:1.0}

#General Damage multiplier for each weapon type.
weapon_damage_multiplier={}

weapon_damage_multiplier[BARE_HAND]=.75
weapon_damage_multiplier[SWORD]=1.0
weapon_damage_multiplier[MACE]=1.2
weapon_damage_multiplier[LONGBOW]=.8
weapon_damage_multiplier[CROSSBOW]=.4
weapon_damage_multiplier[KNIFE]=.8
weapon_damage_multiplier[SPEAR]=.9
weapon_damage_multiplier[STAFF]=.5
weapon_damage_multiplier[GREATSWORD]=1.4
weapon_damage_multiplier[MALLET]=1.88

preferred_range[BARE_HAND]=MELEE_RANGE
preferred_range[SWORD]=SWORD_RANGE
preferred_range[MACE]=SWORD_RANGE
preferred_range[LONGBOW]=BOW_RANGE
preferred_range[CROSSBOW]=BOW_RANGE
preferred_range[KNIFE] = MELEE_RANGE
preferred_range[SPEAR] = POLE_RANGE
preferred_range[STAFF] = POLE_RANGE
preferred_range[GREATSWORD] = SWORD_RANGE
preferred_range[MALLET] = POLE_RANGE


# Stats tuple
stats = (
    "strength", "intelligence", "discipline",
    "agility","charisma","perception",
    )

DEFAULT_STAT=-1


# Gender Handling
GENDER_NEUTRAL ="Neutral"
GENDER_MALE = "Male"
GENDER_FEMALE = "Female"
RACE_NEUTRAL = "None"
pronoun_reflexive={}
pronoun_reflexive[GENDER_NEUTRAL] = "itself"
pronoun_reflexive[GENDER_MALE] = "himself"
pronoun_reflexive[GENDER_FEMALE] = "herself"
pronoun_subject={}
pronoun_subject[GENDER_NEUTRAL] = "it"
pronoun_subject[GENDER_MALE] = "he"
pronoun_subject[GENDER_FEMALE]= "she"
pronoun_object={}
pronoun_object[GENDER_MALE] = "him"
pronoun_object[GENDER_FEMALE] = "her"
pronoun_object[GENDER_NEUTRAL] = "it"
pronoun_possessive={}
pronoun_possessive[GENDER_MALE] ="his"
pronoun_possessive[GENDER_FEMALE] ="her"
pronoun_possessive[GENDER_NEUTRAL] ="its"

#Priorities
HIGHEST_PRIORITY=0
WALKING_PRIORITY=4

#Balance ranges
MIN_BALANCE=-11
MAX_BALANCE=11

#Balance messaging
balance_name={}

balance_name[-11]="Completely Unbalanced"
balance_name[-10]="Wildly unbalanced (-)"
balance_name[-9] ="Wildly unbalanced"
balance_name[-8] ="Wildly unbalanced (+)"
balance_name[-7] ="Unbalanced (-)"
balance_name[-6] ="Unbalanced"
balance_name[-5] ="Unbalanced (+)"
balance_name[-4] ="Slightly unbalanced (-)"
balance_name[-3] ="Slightly unbalanced"
balance_name[-2] ="Slightly unbalanced (+)"
balance_name[-1] = "Neutrally balanced (-)"
balance_name[0]  = "Neutrally balanced"
balance_name[1]  = "Neutrally balanced (+)"
balance_name[2]  = "Better balanced (-)"
balance_name[3]  = "Better balanced"
balance_name[4]  = "Better balanced (+)"
balance_name[5]  = "Well balanced (-)"
balance_name[6]  = "Well balanced"
balance_name[7]  = "Well balanced (+)"
balance_name[8]  = "Superbly balanced (-)"
balance_name[9]  = "Superbly balanced"
balance_name[10] = "Superbly balanced (+)"
balance_name[11] = "Indelibly balanced"

balance_multiplier={}
balance_multiplier[-11]=.5
balance_multiplier[-10]=.7
balance_multiplier[-9] =.7
balance_multiplier[-8] =.7
balance_multiplier[-7] =.8
balance_multiplier[-6] =.8
balance_multiplier[-5] =.8
balance_multiplier[-4] =.9
balance_multiplier[-3] =.9
balance_multiplier[-2] =.9
balance_multiplier[-1] = 1
balance_multiplier[0]  = 1
balance_multiplier[1] =  1
balance_multiplier[2] =  1.1 
balance_multiplier[3] =  1.1
balance_multiplier[4] =  1.1
balance_multiplier[5] =  1.2
balance_multiplier[6] =  1.2
balance_multiplier[7] =  1.2
balance_multiplier[8] =  1.3
balance_multiplier[9] =  1.3
balance_multiplier[10]=  1.3
balance_multiplier[11]=  1.5


#DAMAGE TYPES
IMPACT=1
PUNCTURE=2
SLASH=3
BURN=4
COLD=5
ELECTRIC=6
DIVINE=7
PROFANE=8

damage_match_val = (IMPACT,PUNCTURE,SLASH,BURN,COLD,ELECTRIC,DIVINE,PROFANE)
damage_match_txt = ("impact","puncture","slash","burn","cold","electric","divine","profane")




# Enumerates genders for processing for character configuration
# 0 is the default gender
gender = [
    GENDER_NEUTRAL,
    GENDER_MALE,
    GENDER_FEMALE
    ]


races = [
    RACE_NEUTRAL,
    "Human",
    "Elf",
    "Dwarf",
    "Orc",
    "Wyvernfolk"
    ]


# Prompts (and default values).
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


# Basic configurable options (and default values).
options = {
    "bind_address" : "",  # "" is a special system identifier for * (all)
    "bind_port" : "4000",  # The server's listening port
    "default_start" : "system:default",  # Default starting room
    "wrap_size" : "60",  # Default word-wrap line length
    "verbose" : "yes",  # Display "trivial" log entries?
    "debug" : "no",  # Halt on errors from safe_mode?
    "root_dir" : sigma_path(),  # Where to look for designer modules and XML files
    "players_db" : os.path.join(sigma_path(), "config", "players.db"),  # Location of player database
    "currency" : "gold",  # Currency unit
    }


# Defines system directories for items that are searched dynamically.
directories = {
    "xml_root" : os.path.join(options["root_dir"], "config"),  # XML root directory and location of server.xml
    "tasks_root" : os.path.join(options["root_dir"], "tasks"),  # Root directory for task modules
    "handlers_root" : os.path.join(options["root_dir"], "handlers"),  # Root directory for handler modules
    "orders_root" : os.path.join(options["root_dir"], "classes"),  # Root directory for order modules
    "personas_root" : os.path.join(options["root_dir"], "personas"),  # Root directory for persona modules
    }
