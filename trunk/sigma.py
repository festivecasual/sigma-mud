import asyncore
import sys

import command
import handler
import importer
import network
import task
from world import World
from entities import Player
from archive import Archive
from common import *


def main():
    log("SYSTEM", "Startup in progress")

    log("SYSTEM", "Initializing database")
    Archive()

    log("MODULES", "Inspecting task modules")
    task.load_tasks()

    log("MODULES", "Inspecting handler modules")
    handler.load_handlers()

    log("XML", "Processing server.xml")
    importer.process_xml()

    w = World()

    log("WORLD", "Resolving exits")
    w.resolve_exits()

    log("WORLD", "Resolving populator objects")
    w.resolve_populators()

    log("WORLD", "Resolving placement objects")
    w.resolve_placements()

    log("NETWORK", "Initializing master socket")
    listener = network.ServerSocket()

    log("TASK", "Initializing task modules")
    task.init_tasks()

    log("SYSTEM", "Startup complete, entering main loop")
    while True:
        try:
            asyncore.loop(timeout=0.1, count=1)
            command.process_commands()
            task.run_tasks()
        except KeyboardInterrupt:
            print("")
            log("CONSOLE", "Keyboard interrupt detected")
            break

    log("SYSTEM", "Shutdown in progress")

    log("NETWORK", "Shutting down master socket")
    listener.close()

    log("MODULES", "Deinitializing task modules")
    task.deinit_tasks()

    log("SYSTEM", "Shutdown complete")


def run_tests():
    from test import TestbedServer
    import unittest

    server = TestbedServer()
    server.clear_archive()
    server.start()

    tests = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=3, buffer=True)
    runner.run(tests)
    server.stop()


def players():
    log("SCRIPT", "Booting core server functionality")
    a = Archive()
    handler.load_handlers()
    importer.process_xml()
    log("SCRIPT", "Finished loading core functionality")

    log("SCRIPT", "Retreiving player information from database")
    players = a.list()
    log("SCRIPT", "Loaded %d player%s from database" % (len(players), '' if len(players) == 1 else 's'))
    print

    i = 0
    names = players.keys()
    names.sort()
    for p in names:
        i += 1
        print '%d: %s' % (i, p)
    print

    n = raw_input('Load player index (blank to cancel): ')
    name = None
    try:
        n = int(n)
        if n < 1 or n > len(names):
            print 'Cancelled.'
            sys.exit(0)
        name = names[n - 1]
    except (ValueError, IndexError):
        sys.exit(1)

    player = Player()
    if not a.load(name, player):
        choice = raw_input('Player could not be loaded properly.  Delete? (Y/N): ')
        if choice.upper() == 'Y':
            a.delete(name)
        sys.exit(0)

    print
    print player.name
    print player.gender, player.race
    for stat, value in player.stats.items():
        print ' %s: %d' % (stat, value)
    print
    action = raw_input('Action ([p]assword, [d]elete), [c]ancel): ')
    if action == '':
        sys.exit(0)
    elif 'password'.startswith(action.lower()):
        player.password = encrypt_password(raw_input('New password: '))
        a.save(player)
        print 'Password written.'
    elif 'delete'.startswith(action.lower()):
        confirm = raw_input('Really delete? (Y/N): ')
        if confirm.upper() == 'Y':
            a.delete(name)
            print 'Deletion complete.'
        else:
            print 'Deletion cancelled.'
    else:
        print 'Cancelled.'


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        main()
    elif sys.argv[1] == 'test':
        run_tests()
    elif sys.argv[1] == 'players':
        players()
