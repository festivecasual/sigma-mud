import asyncore
import world
from common import *

def task_info():
	return ('Server Status Update', 'Sigma Internal', "1.0", 300)

def task_init():
	pass

def task_execute():
	log("STATUS", str(len(asyncore.socket_map) - 1) + " active connection(s), " + str(len(world.players)) + " login(s)")

def task_deinit():
	pass

