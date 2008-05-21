import pickle
import world
from common import *

def task_info():
	return ('Instance Denizens and Items', 'Sigma Internal', '1.0', 15)

def task_init():
	task_execute()

def task_execute():
	for current in world.populators:
		if not world.denizens.has_key(id(current.instance)):
			current.instance = pickle.loads(current.denizen)
			
			world.denizens[id(current.instance)] = current.instance
			current.target.characters.append(current.instance)
	
	for current in world.placements:
		if not world.items.has_key(id(current.instance)):
			current.instance = pickle.loads(current.item)
			
			world.items[id(current.instance)] = current.instance
			current.target.contents.append(pickle.loads(current.item))

def task_deinit():
	pass
