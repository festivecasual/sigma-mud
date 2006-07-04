import glob, os.path, imp, sys, time
from common import *

tasks = []

def load_tasks():
	task_modules = glob.glob(options["tasks_root"] + "/*.py")
	for task_file in task_modules:
		source = os.path.basename(task_file)
		name = os.path.splitext(source)[0]

		try:
			imp.load_source(name, options["tasks_root"] + "/" + source)

			task = sys.modules[name]
			task_name, task_author, task_version, task_interval = task.task_info()

			log("TASK", "Loading [" + task_name + "] (" + task_author + ", " + task_version + ")")

			tasks.append([task, time.time(), task.task_info()[3]])
			tasks[-1][0].task_init()
		except:
			log("ERROR", "Task module [" + source + "] broken, change .py extension to disable")

def run_tasks():
	for task in tasks:
		if time.time() >= (task[1] + task[2]):
			try:
				task[0].task_execute()
			except:
				log("ERROR", "Exception thrown in task_execute() for [" + task[0].task_info()[0] + "]")

			task[1] = time.time()

def deinit_tasks():
	for task in tasks:
		log("TASK", "Shutting down [" + task[0].task_info()[0] + "]")

		try:
			task[0].task_deinit()
		except:
			log("ERROR", "Exception thrown in task_deinit() for [" + task[0].task_info()[0] + "]")
