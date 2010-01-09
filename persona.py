import glob
import os.path
import imp

import libsigma
from common import *


personas = {}


def load_personas():
    persona_modules = glob.glob(os.path.join(directories["personas_root"], '*.py'))
    for persona_file in persona_modules:
        source = os.path.basename(persona_file)
        module_name = 'persona_' + os.path.splitext(source)[0]

        p = libsigma.safe_mode(imp.load_source, module_name, persona_file)
        if not p:
            log('PERSONA', 'Not loading [%s]: errors detected' % source, problem=True)
            continue
        try:
            p_name = p.name
            p_events = p.events
        except AttributeError:
            log('PERSONA', 'Persona module [%s] is missing one or more required members' % source, problem=True)
        else:
            personas[p_name] = p_events
            log('PERSONA', 'Loaded persona [%s]' % p.name)
