## @package update
#  Output a server status update to the server console.
#  
#  @ingroup task

import asyncore
import world
from common import *

## Returns name, authorship, version, and period length (in seconds).
def task_info():
	return ('Server Status Update', 'Sigma Internal', '1.0', 300)

## Defines the code to be run upon loading the task.
def task_init():
	pass

## Defines the code to be run at each execution period.
def task_execute():
	log("STATUS", str(len(asyncore.socket_map) - 1) + " active connection(s), " + str(len(world.players)) + " login(s)")

## Defines the code to be run upon shutdown of the server.
def task_deinit():
	pass
