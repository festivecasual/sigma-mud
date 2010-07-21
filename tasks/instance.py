import pickle

import world
import libsigma
from common import *


# Proper name of task
name = 'Instance Denizens and Items'
interval = 360


# Defines the code to be run upon loading the task.
def task_init():
    task_execute()


# Defines the code to be run at each execution period.
def task_execute():
    for current in world.populators:
        if not world.denizens.has_key(id(current.instance)):
            current.instance = pickle.loads(current.denizen)

            world.denizens[id(current.instance)] = current.instance
            libsigma.enter_room(current.instance, current.target)

    for current in world.placements:
        if not id(current.instance) in [id(i) for i in current.target.contents]:
            current.instance = pickle.loads(current.item)
            current.instance.quantity=current.quantity
            world.items[id(current.instance)] = current.instance
            current.target.contents.append(current.instance)


# Defines the code to be run upon shutdown of the server.
def task_deinit():
    pass
