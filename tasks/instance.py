import pickle
import world
from common import *

def task_info():
	return ('Instance Denizens and Items', 'Sigma Internal', "1.0", 100)

def task_init():
	task_execute()

def task_execute():
	for current in world.populators:
		current.target.characters.append(pickle.loads(current.denizen))
	
	for current in world.placements:
		current.target.contents.append(pickle.loads(current.item))

def task_deinit():
	pass
