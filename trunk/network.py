import asyncore
import asynchat
import socket
import sys
import string

import world, command, archive, libsigma
from common import *

class client_socket(asynchat.async_chat):
    def __init__(self, connection):
        asynchat.async_chat.__init__(self, connection)

        # Holds all pending text (awaiting a newline from client).
        self.buffer = ''

        self.set_terminator('\n')

        # Retains the player class tied to this socket.
        self.parent = world.player(self)

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
        if self.parent.location:
            libsigma.report(libsigma.ROOM, "$actor has left the game.", self.parent)
            self.parent.location.characters.remove(self.parent)

        if self.parent in world.players:
            archive.player_save(self.parent)
            world.players.remove(self.parent)

        log("NETWORK", "Client at " + self.addr[0] + " closed connection")
        self.parent.socket = None
        self.close()

    def handle_accept(self):
        pass


class server_socket(asyncore.dispatcher):
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
        client_socket(accept_socket)