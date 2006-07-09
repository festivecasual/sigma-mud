import time, sha

def log(label, text, trivial = False):
	if not (trivial and (options["verbose"] == "no")):
		print "%-10s | %s" % (label, text)

def time_string():
	return time.strftime("%H:%M:%S")

def encrypt_password(password):
	crypter = sha.new(password)
	return crypter.digest()

# Play state constants
STATE_NULL       = 0
STATE_INIT       = 1
STATE_NAME       = 2
STATE_PASSWORD   = 3
STATE_PLAYING    = 4

# Prompts (and default values)
prompts =	{
		 STATE_INIT : "\r\n\r\nWelcome to the Sigma Environment v. 0.0.1!\r\n\r\n",
		 STATE_NAME : "Please enter your name: ",
		 STATE_PASSWORD : "Your password: ",
		 STATE_PLAYING : "\r\n> "
		}

# Basic configurable options (and default values)
options =	{
		 "bind_address" : "",				# "" is a special system identifier for * (all)
		 "bind_port" : "4000",				# The server's listening port
		 "players_db" : "./data/players.db",		# Location of players database
		 "verbose" : "yes"				# Display "trivial" log entries?
		}

root_dir = "."
directories =	{
		 "xml_root" : root_dir + "/data",		# XML root directory and location of server.xml
		 "tasks_root" : root_dir + "/tasks",		# Root directory for task modules
		 "handlers_root" : root_dir + "/handlers"	# Root directory for handler modules
		}
