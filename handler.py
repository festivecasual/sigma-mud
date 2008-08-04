## @package handler
#  Defines the handler framework for input-driven execution.

## @defgroup handler Built-In Handlers
#  Handlers included as default infrastructure within the environment.
#
#  @sa The handler framework defined in handler.py.

import glob, os.path, imp, sys, inspect
import libsigma
from common import *

## Holds list of all available handler functions.
functions = {}

## Holds mappings from typed commands to handlers.
mappings = []

## Stores all available "special" shortcut commands.
specials = {
	"apostrophe" : None,
	"comma" : None,
	"colon" : None,
	"period" : None
	}

## Detect if the passed function is a valid handler (as defined by the \@handler decorator).
#
#  @param function The function to check.
def is_handler(function):
	return hasattr(function, '__handler__')

## Process the handlers/ directory and load handlers into the master handler list.
def load_handlers():
	handler_modules = glob.glob(directories["handlers_root"] + "/*.py")
	for handler_file in handler_modules:
		source = os.path.basename(handler_file)
		name = "handler_" + os.path.splitext(source)[0]

		try:
			imp.load_source(name, directories["handlers_root"] + "/" + source)
			
			count = 0
			new_handlers = inspect.getmembers(sys.modules[name], inspect.isfunction)
			for key, function in new_handlers:
				if is_handler(function):
					functions[key] = function
					count += 1
			
			log("HANDLERS", "Loaded " + str(count) + " handler(s) from [" + source + "]")

		except:
			log("  *  ERROR", "Handler module [" + source + "] is not functional")
			continue
