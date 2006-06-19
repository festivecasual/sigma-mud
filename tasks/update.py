import common

def task_info():
	return ('Server Status Update', 'Sigma Internal', 1, 1)

def task_execute():
	log("STATUS", "This is a statistics update")
