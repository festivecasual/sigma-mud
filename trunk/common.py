## @package common
#  Utility functions and structure definitions.
#
#  Functions and structures within common are not designer-facing,
#  as those items are to be placed in libsigma.
#
#  @sa Consult libsigma for additional utility features.

import time, datetime, hashlib, os.path, sys

## Construct a log entry for the server console.
#
#  @param label The type of log message.
#  @param text The log message to display.
#  @param trivial Set to True when the log message should be shown only in "verbose" mode.
def log(label, text, trivial = False):
	if not (trivial and (options["verbose"] == "no")):
		print "%-10s | %s" % (label, text)

## Return a formatted string to indicate the current time.
def time_string():
	return time.strftime("%H:%M:%S")

## Returns a formatted string with both current date and time
def date_time_string():
	return time.strftime("%Y/%m/%d %H:%M:%S")
		
## Return an encrypted (SHA hashed) password.
#
#  @param password The plain-text password to encrypt.
def encrypt_password(password):
	crypter = hashlib.sha1()
	crypter.update(password)
	return crypter.digest()

## Remove the excess whitespace from a string (for XML CDATA).
#
#  @param text The text to process.
#  @return The whitespace-stripped \c text.
def strip_whitespace(text):
	new = text
	old = ""

	while new != old:
		old = new
		for c in whitespace:
			new = new.replace(c, " ")

	return new.strip()

## Wrap text at a specified width.
#
#  @param text The text to wrap.
#  @param width The width to wrap
#  @return The processed text.
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

## Ignorable whitespace (used by strip_whitespace)
#
#  Double-space should go last for the sake of efficiency
whitespace = ["\t", "\n", "\f", "\r", "\v", "  "]

## Null play state
STATE_NULL       		 = 0
## Initial play state
STATE_INIT       		 = 1
## Play state for typing name
STATE_NAME      		 = 2
## Play state for typing password
STATE_PASSWORD   		 = 3
## Play state for normal gameplay
STATE_PLAYING   		 = 4
##  Play states for configuring player

STATE_CONFIG_NAME		 = 5
# Play state for configuring password
STATE_CONFIG_PASSWORD    = 6
# Play state for configuring character attributes
STATE_CONFIG_CHAR 		 = 7
# Play state for configuring character statistics
STATE_CONFIG_STATS      =  8

##Combat States
COMBAT_STATE_INITIALIZING = 1
COMBAT_STATE_ENGAGING = 2
COMBAT_STATE_FIGHTING_C1_ACTION = 3
COMBAT_STATE_FIGHTING_C2_ACTION = 4
COMBAT_STATE_INTERMISSION = 5

#Combat actions
COMBAT_ACTION_ATTACKING=1

## Direction: North
DIR_NORTH        =  0
## Direction: Northeast
DIR_NORTHEAST    =  1
## Direction: East
DIR_EAST         =  2
## Direction: Southeast
DIR_SOUTHEAST    =  3
## Direction: South
DIR_SOUTH        =  4
## Direction: Southwest
DIR_SOUTHWEST    =  5
## Direction: West
DIR_WEST         =  6
## Direction: Northwest
DIR_NORTHWEST    =  7
## Direction: Up
DIR_UP           =  8
## Direction: Down
DIR_DOWN         =  9
## Direction: Enter
DIR_ENTER        = 10
## Direction: Leave
DIR_LEAVE        = 11

## Total number of directions.
NUM_DIRS         = 12

## Tuple for matching direction text
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

## Tuple for matching direction constants
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


## States for doors

DOOR_OPEN = 0

DOOR_CLOSED = 1

DOOR_LOCKED = 2

# Wear places and limit for items of this type to be worn
worn_limit ={}
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

BACK_WORN = 10 ## cloaks/robes and such
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


#Weapon Types
NOT_A_WEAPON= 0
SWORD=1
MACE=2
LONGBOW=3
CROSSBOW=4
KNIFE=4
SPEAR=5
STAFF=6
GREATSWORD=7
MALLET=8
BARE_HAND=9

weapon_match_val = (SWORD,MACE,LONGBOW,CROSSBOW,KNIFE,SPEAR,STAFF,GREATSWORD,MALLET, BARE_HAND)
weapon_match_txt = ("sword","mace","longbow","knife","spear","staff","greatsword","mallet","bare handed")


#Combat Ranges. Difference between the integers is significant. Represents distance.
NOT_IN_COMBAT=0
MELEE_RANGE=1
SWORD_RANGE=2
POLE_RANGE=4
BOW_RANGE=6

range_match_txt=("melee", "sword","pole","bow")
range_match_val=(MELEE_RANGE,SWORD_RANGE,POLE_RANGE,BOW_RANGE)

#range for weapon types
weapon_range = {}
preferred_range ={}

#Damage multiplayers at differing ranges
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


#stats tuple
stats = ("strength", "intelligence", "discipline", "agility","charisma","perception")

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

#Enumerates genders for processing for character configuration
#0 is the default gender
gender = [GENDER_NEUTRAL,GENDER_MALE,GENDER_FEMALE]

races = [RACE_NEUTRAL, "Human", "Elf", "Dwarf", "Orc", "Wyvernfolk" ]

## Prompts (and default values).
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

## Basic configurable options (and default values).
options = {
	"bind_address" : "",  # "" is a special system identifier for * (all)
	"bind_port" : "4000",  # The server's listening port
	"players_db" : "./config/players.db",  # Location of players database
	"default_start" : "system:default",  # Default starting room
	"wrap_size" : "60",  # Default word-wrap line length
	"verbose" : "yes",  # Display "trivial" log entries?
	"debug" : "no",  # Halt on errors from safe_mode?
	"root_dir" : sigma_path(),  # Where to look for designer modules and XML files
	}

## Defines the relative root for all file access.
root_dir = "."

## Defines system directories.
directories = {
	"xml_root" : options["root_dir"] + "/config",  # XML root directory and location of server.xml
	"tasks_root" : options["root_dir"] + "/tasks",  # Root directory for task modules
	"handlers_root" : options["root_dir"] + "/handlers",  # Root directory for handler modules
	"orders_root" : options["root_dir"] + "/classes",  # Root directory for order modules
	}

