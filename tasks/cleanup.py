import world
from common import *
#import libsigma

name = 'Duration Cleanup'
interval= 450

def task_init():
	pass

def task_execute():
	c=0 
	for p in world.players:
		for d in p.waits:
			if (d.duration_expired()):
				p.waits.remove(d)
				c+=1
	#log("CLEANUP", str(c)+ " stale durations cleaned")
	

def task_deinit():
	pass