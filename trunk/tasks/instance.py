from world import World
from entities import Denizen, Item
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
    w = World()
    for current in w.populators:
        if not w.denizens.has_key(current.instance):
            denizen = Denizen(current.denizen)
            current.instance = denizen.id
            w.denizens[denizen.id] = denizen
            libsigma.enter_room(denizen, current.target)

    for current in w.placements:
        if not current.instance in [i.id for i in current.target.contents]:
            item = Item(current.item)
            item.quantity = current.quantity
            current.instance = item.id
            w.items[item.id] = item
            current.target.contents.append(item)


# Defines the code to be run upon shutdown of the server.
def task_deinit():
    pass
