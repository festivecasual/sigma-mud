## @package instance
#  Populate the world structure with templated items and denizens.
#  
#  @ingroup task

import pickle
import world
from common import *

## Returns name, authorship, version, and period length (in seconds).
def task_info():
	return ('Instance Denizens and Items', 'Sigma Internal', '1.0', 300)

## Defines the code to be run upon loading the task.
def task_init():
	task_execute()

## Defines the code to be run at each execution period.
def task_execute():
	for current in world.populators:
		if not world.denizens.has_key(id(current.instance)):
			current.instance = pickle.loads(current.denizen)
			
			world.denizens[id(current.instance)] = current.instance
			current.target.characters.append(current.instance)
	
	for current in world.placements:
		if not id(current.instance) in [id(i) for i in current.target.contents]:
			current.instance = pickle.loads(current.item)
			
			world.items[id(current.instance)] = current.instance
			current.target.contents.append(current.instance)

## Defines the code to be run upon shutdown of the server.
def task_deinit():
	pass
