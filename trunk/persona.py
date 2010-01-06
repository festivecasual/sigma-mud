import glob
import os.path
import imp
from common import *


personas = {}


def load_personas():
    persona_modules = glob.glob(os.path.join(directories["personas_root"], "*.py"))
    for persona_file in persona_modules:
        source = os.path.basename(persona_file)
        module_name = 'persona_' + os.path.splitext(os.path.basename(persona_file))[0]

        try:
            p = imp.load_source(module_name, os.path.join(directories["personas_root"], source))
            personas[p.name] = p.events
            log("PERSONA", "Loaded persona [%s]" % p.name)
        except:
            log("  *  ERROR", "Persona module [%s] is not functional" % source)
            continue
