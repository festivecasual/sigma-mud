import glob, os.path, imp, sys
from common import *

handlers = {}

def load_handlers():
	handler_modules = glob.glob(options["handlers_root"] + "/*.py")
	for handler_file in handler_modules:
		source = os.path.basename(handler_file)
		name = os.path.splitext(source)[0]

		try:
			imp.load_source(name, options["handlers_root"] + "/" + source)

			new_handlers = sys.modules[name].register_handlers()
			handlers.update(new_handlers)

			log("HANDLERS", "Loading " + str(len(new_handlers)) + " handler(s) from [" + source + "]")
		except:
			log("ERROR", "Handler module [" + source + "] broken, change .py extension to disable")
