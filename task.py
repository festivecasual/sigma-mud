import glob, os.path, imp, sys, time
import libsigma
from common import *

tasks = []

def load_tasks():
	task_modules = glob.glob(directories["tasks_root"] + "/*.py")
	for task_file in task_modules:
		source = os.path.basename(task_file)
		name = "task_" + os.path.splitext(source)[0]

		try:
			imp.load_source(name, directories["tasks_root"] + "/" + source)

			f_info = sys.modules[name].task_info
			f_init = sys.modules[name].task_init
			f_execute = sys.modules[name].task_execute
			f_deinit = sys.modules[name].task_deinit
		except:
			log("  *  ERROR", "Task module [" + source + "] is not functional")
			continue

		ret = libsigma.safe_mode(f_info)
		if ret:
			task_name, task_author, task_version, task_interval = ret
			libsigma.safe_mode(f_init)

		log("TASK", "Loading [" + task_name + "] (" + task_author + ", " + task_version + ")")
		tasks.append([sys.modules[name], time.time(), task_interval])

def run_tasks():
	for task in tasks:
		if time.time() >= (task[1] + task[2]):
			libsigma.safe_mode(task[0].task_execute)
			task[1] = time.time()

def deinit_tasks():
	for task in tasks:
		log("TASK", "Shutting down [" + task[0].task_info()[0] + "]")

		libsigma.safe_mode(task[0].task_deinit)
