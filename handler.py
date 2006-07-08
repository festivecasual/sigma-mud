import glob, os.path, imp, sys
import libsigma
from common import *

handlers = {}

def load_handlers():
	handler_modules = glob.glob(options["handlers_root"] + "/*.py")
	for handler_file in handler_modules:
		source = os.path.basename(handler_file)
		name = "handler_" + os.path.splitext(source)[0]

		try:
			imp.load_source(name, options["handlers_root"] + "/" + source)
		except:
			log("  *  ERROR", "Handler module [" + source + "] is not functional")
			continue

		new_handlers = libsigma.safe_mode(sys.modules[name].register_handlers)
		if new_handlers:
			handlers.update(new_handlers)
			log("HANDLERS", "Loading " + str(len(new_handlers)) + " handler(s) from [" + source + "]")