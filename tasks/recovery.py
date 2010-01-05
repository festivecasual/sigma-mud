import world
import libsigma
from common import *


# Proper name of task
name = 'Passive Recovery'
interval = 60  # Provisional


# Defines the code to be run upon loading the task.
def task_init():
    pass


# Defines the code to be run at each execution period.
def task_execute():
    for p in world.players:
        if p.state >= STATE_PLAYING:
            p.HP += 3


# Defines the code to be run upon shutdown of the server.
def task_deinit():
    pass
