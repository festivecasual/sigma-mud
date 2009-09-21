import asyncore

import world
from common import *


# Proper name of task
name = 'Server Status Update'
interval = 300


# Defines the code to be run upon loading the task.
def task_init():
    pass


# Defines the code to be run at each execution period.
def task_execute():
    log("STATUS", str(len(asyncore.socket_map) - 1) + " active connection(s), " + str(len(world.players)) + " login(s)")


# Defines the code to be run upon shutdown of the server.
def task_deinit():
    pass
