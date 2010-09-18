import asyncore

from world import World
from common import *


# Proper name of task
name = 'Server Status Update'
interval = 300


# Defines the code to be run upon loading the task.
def task_init():
    pass


# Defines the code to be run at each execution period.
def task_execute():
    w = World()
    if len(w.players) > 0:
        log("STATUS", "%d active connection(s) + %d login(s)" % (len(asyncore.socket_map) - 1, len(w.players)))


# Defines the code to be run upon shutdown of the server.
def task_deinit():
    pass
