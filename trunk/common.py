## @package common
#  Utility functions and structure definitions.
#
#  Functions and structures within common are not designer-facing,
#  as those items are to be placed in libsigma.
#
#  @sa Consult libsigma for additional utility features.

import time, datetime, sha, os.path, sys

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

		
##=======
## Return an encrypted (SHA hashed) password.
#
#  @param password The plain-text password to encrypt.
##>>>>>>> .r78
def encrypt_password(password):
	crypter = sha.new(password)
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
#  @param width The width to wrap, or -1 to wrap at the default wrap width.
#  @return The processed text.
def wordwrap(text, width = -1):
	working = text
	wrapped = ""
	
	if width == -1:
		width = options["wrap-size"]
	
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
	elif(int(int_val)%10==1 and int(int_val)%100!=13):
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
STATE_NULL       = 0
## Initial play state
STATE_INIT       = 1
## Play state for typing name
STATE_NAME       = 2
## Play state for typing password
STATE_PASSWORD   = 3
## Play state for normal gameplay
STATE_PLAYING    = 4

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

## Prompts (and default values).
prompts = {
	STATE_INIT : "\r\n\r\nWelcome to the Sigma Environment v. 0.0.1!\r\n\r\n",
	STATE_NAME : "Please enter your name: ",
	STATE_PASSWORD : "Your password: ",
	STATE_PLAYING : "\r\n> ",
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
