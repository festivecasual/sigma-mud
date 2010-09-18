from world import World
from common import *


name = 'Duration Cleanup'
interval = 450


def task_init():
    pass


def task_execute():
    c = 0
    w = World()
    for p in w.players:
        for d in p.waits:
            if (d.duration_expired()):
                p.waits.remove(d)
                c += 1


def task_deinit():
    pass
