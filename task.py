import glob, os.path, imp, sys, time
import libsigma
from common import *

tasks = []

def load_tasks():
	task_modules = glob.glob(options["tasks_root"] + "/*.py")
	for task_file in task_modules:
		source = os.path.basename(task_file)
		name = "task_" + os.path.splitext(source)[0]

		try:
			imp.load_source(name, options["tasks_root"] + "/" + source)
			ret = libsigma.safe_mode(sys.modules[name].task_info)
			if ret:
				task_name, task_author, task_version, task_interval = ret
				log("TASK", "Loading [" + task_name + "] (" + task_author + ", " + task_version + ")")
				tasks.append([sys.modules[name], time.time(), task_interval])
				libsigma.safe_mode(tasks[-1][0].task_init)
		except:
			log("  *  ERROR", "Task module [" + source + "] is not functional")
			continue

def run_tasks():
	for task in tasks:
		if time.time() >= (task[1] + task[2]):
			libsigma.safe_mode(task[0].task_execute)
			task[1] = time.time()

def deinit_tasks():
	for task in tasks:
		log("TASK", "Shutting down [" + task[0].task_info()[0] + "]")

		libsigma.safe_mode(task[0].task_deinit)
