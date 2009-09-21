import glob
import os.path
import imp
import sys
import inspect

import libsigma
from common import *


functions = {}
mappings = []
specials = {
    "apostrophe" : None,
    "comma" : None,
    "colon" : None,
    "period" : None
    }


def is_handler(function):
    return hasattr(function, '__handler__')


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
