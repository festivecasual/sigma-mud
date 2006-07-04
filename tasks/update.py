from common import *

def task_info():
	return ('Server Status Update', 'Sigma Internal', "1.0", 120)

def task_init():
	pass

def task_execute():
	log("STATUS", "This is a statistics update")

def task_deinit():
	pass

