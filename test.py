import asyncore
import socket
import unittest
import os.path
import time
from xml.etree import ElementTree

import task
import handler
import importer
import network
import command
from calendar import Calendar
from world import World
from archive import Archive
from common import *


@singleton
class TestbedServer(object):
    def __init__(self):
        self.listener = None
        options["default_start"] = "test:room1"
        options["players_db"] = os.path.join(sigma_path(), "config", "test", "players.db")
        options["verbose"] = "silent"
        options["debug"] = "yes"

        self.px = lambda x: ElementTree.parse(x).getroot()
        self.standard = lambda p: self.px(os.path.join(directories["xml_root"], p))
        self.testbase = lambda p: self.px(os.path.join(sigma_path(), "config", "test", p))

        self.pool = []

    def clear_archive(self):
        a = Archive()
        players = a.list()
        for p in players.keys():
            a.delete(p)

    def connection(self, index=1):
        while index > len(self.pool):
            self.pool.append(Socket())
        return self.pool[index - 1]

    def flush_pool(self):
        [sock.close() for sock in self.pool]
        self.pool = []

    def map_login(self, name):
        w = World()
        for p in w.players:
            if p.name == name:
                return p
        return None

    def start(self):
        self.listener = network.ServerSocket()
        Archive()
        task.load_tasks()
        handler.load_handlers()

        self.process_imports()

        w = World()
        w.calendars.append(Calendar(self.standard('calendar.xml'), 'Test Default'))
        w.resolve_exits()
        w.resolve_populators()
        w.resolve_placements()

        task.init_tasks()

    def process_imports(self):
        importer.process_handlers(self.standard('handlers-map.xml'))
        importer.process_stance(self.standard('stances.xml'))
        importer.process_area(self.testbase('area.xml'), 'test')

    def pulse(self):
        asyncore.loop(timeout=0.1, count=1)
        command.process_commands()

    def zip_tasks(self):
        for t, i in task.tasks.items():
            task.tasks[t] = (i[0], time.time() - i[2], i[2], i[3])

    def run_tasks(self):
        task.run_tasks()
        self.pulse()
        self.pulse()
        self.pulse()

    def stop(self):
        self.flush_pool()
        task.deinit_tasks()
        self.listener.close()
        self.listener = None


class Socket(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(('127.0.0.1', int(options["bind_port"])))
        self.buffer = ''
        self.script = ''

        self.server = TestbedServer()
        self.server.pulse()  # Connect
        self.server.pulse()  # Greeting
        self.server.pulse()  # Extra
        self.server.pulse()  # Extra

    def send(self, data):
        self.script += data
        asyncore.dispatcher.send(self, data)

    def sendline(self, line):
        self.send(line + '\r\n')
        self.server.pulse()  # Process
        self.server.pulse()  # Respond
        self.server.pulse()  # Extra
        self.server.pulse()  # Extra

    def sendlines(self, *lines):
        [self.sendline(line) for line in lines]

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        recv = self.recv(8192)
        self.script += recv

    def writable(self):
        return (len(self.buffer) > 0)

    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]
