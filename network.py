import asyncore
import asynchat
import socket
import sys
import string

import command
import libsigma
from archive import Archive
from entities import Player
from world import World
from common import *


class ClientSocket(asynchat.async_chat):
    def __init__(self, connection):
        asynchat.async_chat.__init__(self, connection)

        # Holds all pending text (awaiting a newline from client).
        self.buffer = ''

        self.set_terminator('\n')

        # Retains the player class tied to this socket.
        self.parent = Player(self)

    def collect_incoming_data(self, data):
        for char in data:
            if char == '\b' and len(self.buffer) > 0:
                self.buffer = self.buffer[:-1]
            elif char == '\b' or char == '\r': pass
            elif char in string.printable:
                self.buffer += char
                if self.parent.state == STATE_PASSWORD:
                    self.parent.send('\b \b')

    def found_terminator(self):
        data = self.buffer
        self.buffer = ''
        command.accept_command(self.parent, data)

    def handle_close(self):
        # Shunt output to parent (avoids recursion in simultaneous logouts)
        self.parent.send = lambda s: None

        if self.parent.location:
            libsigma.report(libsigma.ROOM, "$actor has left the game.", self.parent)
            self.parent.location.characters.remove(self.parent)

        w = World()
        if self.parent in w.players:
            a = Archive()
            a.save(self.parent)
            w.players.remove(self.parent)

        log("NETWORK", "Client at %s closed connection" % self.addr[0])
        self.parent.socket = None
        self.close()

    def handle_accept(self):
        pass


class ServerSocket(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)

        try:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.bind((options["bind_address"], int(options["bind_port"])))
            self.listen(5)
        except:
            log("FATAL", "Error initializing socket")
            sys.exit(1)

    def handle_accept(self):
        accept_socket, address = self.accept()
        log("NETWORK", "Connection received from " + address[0])
        ClientSocket(accept_socket)
