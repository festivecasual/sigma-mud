import random

import libsigma
from world import World
from common import *


# Proper name of task
name = 'Denizen Locomotion'
interval = 60


# Defines the code to be run upon loading the task.
def task_init():
    pass


# Defines the code to be run at each execution period.
def task_execute():
    w = World()
    for current in w.populators:
        if current.instance in w.denizens and 'mobile' in current.flags:
            active_denizen = w.denizens[current.instance]

            choices = [None]
            choices.extend(libsigma.open_exits(active_denizen.location))

            selection = random.choice(choices)
            if active_denizen.engaged:
                selection=None

            if (selection != None):
                if active_denizen.location.altmsg[selection]!=None:
                    libsigma.report(libsigma.ROOM, "$actor just went " + active_denizen.location.altmsg[selection] + ".", active_denizen )
                elif (libsigma.dir2txt(selection) =='leave'):
                    libsigma.report(libsigma.ROOM, "$actor just went out.", active_denizen)
                elif (libsigma.dir2txt(selection) == 'enter'):
                    libsigma.report(libsigma.ROOM, "$actor just went in.", active_denizen)
                else:
                    libsigma.report(libsigma.ROOM, "$actor just went " + libsigma.dir2txt(selection) + ".", active_denizen)
                libsigma.enter_room(active_denizen, active_denizen.location.exits[selection])
                libsigma.report(libsigma.ROOM, "$actor has entered the room.", active_denizen)


# Defines the code to be run upon shutdown of the server.
def task_deinit():
    pass
