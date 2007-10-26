import time, sha

def log(label, text, trivial = False):
	if not (trivial and (options["verbose"] == "no")):
		print "%-10s | %s" % (label, text)

def time_string():
	return time.strftime("%H:%M:%S")

def encrypt_password(password):
	crypter = sha.new(password)
	return crypter.digest()

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

# Ignorable whitespace (used by strip_whitespace)
# Double-space should go last for the sake of efficiency
whitespace = ["\t", "\n", "\f", "\r", "\v", "  "]

# Play state constants
STATE_NULL       = 0
STATE_INIT       = 1
STATE_NAME       = 2
STATE_PASSWORD   = 3
STATE_PLAYING    = 4

# Direction constants
DIR_NORTH        =  0
DIR_NORTHEAST    =  1
DIR_EAST         =  2
DIR_SOUTHEAST    =  3
DIR_SOUTH        =  4
DIR_SOUTHWEST    =  5
DIR_WEST         =  6
DIR_NORTHWEST    =  7
DIR_UP           =  8
DIR_DOWN         =  9
DIR_ENTER        = 10
DIR_LEAVE        = 11

NUM_DIRS         = 12

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
	"leave"
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
	DIR_LEAVE
	)

# Prompts (and default values)
prompts = {
	STATE_INIT : "\r\n\r\nWelcome to the Sigma Environment v. 0.0.1!\r\n\r\n",
	STATE_NAME : "Please enter your name: ",
	STATE_PASSWORD : "Your password: ",
	STATE_PLAYING : "\r\n> "
	}

# Basic configurable options (and default values)
options = {
	"bind_address" : "",  # "" is a special system identifier for * (all)
	"bind_port" : "4000",  # The server's listening port
	"players_db" : "./config/players.db",  # Location of players database
	"default_start" : "ravren:100",  # Default starting room
	"wrap_size" : "60",  # Default word-wrap line length
	"verbose" : "yes"  # Display "trivial" log entries?
	}

root_dir = "."
directories = {
	"xml_root" : root_dir + "/config",  # XML root directory and location of server.xml
	"tasks_root" : root_dir + "/tasks",  # Root directory for task modules
	"handlers_root" : root_dir + "/handlers"  # Root directory for handler modules
	}
