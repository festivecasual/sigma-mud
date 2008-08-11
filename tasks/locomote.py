## @package locomote
#  Allow all denizens flagged "mobile" to move to another room
#  
#  @ingroup task

import random
import world, libsigma
from common import *

## Proper name of task
name = 'Denizen Locomotion'

## Interval of task (in seconds)
interval = 60

## Defines the code to be run upon loading the task.
def task_init():
	pass

## Defines the code to be run at each execution period.
def task_execute():
	for current in world.populators:
		if world.denizens.has_key(id(current.instance)) and 'mobile' in current.flags:
			active_denizen = world.denizens[id(current.instance)]

			choices = [None]
			choices.extend(libsigma.exits(active_denizen.location))

			selection = random.choice(choices)
			
			if (selection != None):
				if (libsigma.dir2txt(selection) =='leave'):
					libsigma.report(libsigma.ROOM, "$actor just went out.", active_denizen)
				elif (libsigma.dir2txt(selection) == 'enter'):
					libsigma.report(libsigma.ROOM, "$actor just went in.", active_denizen)
				else:
					libsigma.report(libsigma.ROOM, "$actor just went " + libsigma.dir2txt(selection) + ".", active_denizen)					
				libsigma.enter_room(active_denizen, active_denizen.location.exits[selection])
				libsigma.report(libsigma.ROOM, "$actor has entered the room.", active_denizen)

## Defines the code to be run upon shutdown of the server.
def task_deinit():
	pass
