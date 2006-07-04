import time

def log(label, text):
	print "%-10s | %s" % (label, text)

def time_string():
	return time.strftime("%H:%M:%S")

# Play state constants
STATE_NULL       = 0
STATE_INIT_NAME  = 1
STATE_NAME       = 2
STATE_PASSWORD   = 3
STATE_PLAYING    = 4

# Prompts (and default values)
prompts =	{
		 STATE_INIT_NAME : "Welcome to the Sigma Environment v. 0.0.0!\r\n\r\n",
		 STATE_NAME : "Please enter your name: ",
		 STATE_PASSWORD : "Your password: ",
		 STATE_PLAYING : "> "
		}

# Basic options (and default values)
options =	{
		 "remote_address" : "",  # Special system identifier for 127.0.0.1
		 "tasks_root" : "./tasks"  # Root directory for task modules
		}
