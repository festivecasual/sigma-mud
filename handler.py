import glob
import sys
import os.path
import imp

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


def load_handlers():
    handler_modules = glob.glob(os.path.join(directories["handlers_root"], "*.py"))
    for handler_file in handler_modules:
        n = len(functions)
        source = os.path.basename(handler_file)
        module_name = 'handler_' + os.path.splitext(source)[0]

        h = libsigma.safe_mode(imp.load_source, module_name, handler_file)
        if h:
            log("HANDLER", "Loaded %d handler(s) from [%s]" % (len(functions) - n, source))
        else:
            log("HANDLER", "Handler module [%s] is not functional" % source, problem=True)
            continue
