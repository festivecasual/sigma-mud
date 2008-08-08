## @package task
#  Defines the task framework for scheduled periodic execution.

## @defgroup task Built-In Tasks
#  Tasks included as default infrastructure within the environment.
#
#  @sa The task framework is defined in task.py.

import glob, os.path, imp, sys, time
import libsigma
from common import *

## Holds all loaded tasks for periodic processing.
tasks = {}

## Process the tasks/ directory and load tasks into master task list.
def load_tasks():
	task_modules = glob.glob(directories["tasks_root"] + "/*.py")
	for task_file in task_modules:
		source = os.path.basename(task_file)
		module_name = "task_" + os.path.splitext(source)[0]

		try:
			imp.load_source(module_name, directories["tasks_root"] + "/" + source)

			task_name = sys.modules[module_name].name
			task_interval = sys.modules[module_name].interval
			
			f_init = sys.modules[module_name].task_init
			f_execute = sys.modules[module_name].task_execute
			f_deinit = sys.modules[module_name].task_deinit
		except:
			log("  *  ERROR", "Task module [" + source + "] is not functional")
			continue

		log("TASK", "Loading task [" + task_name + "]")
		tasks[task_name] = (sys.modules[module_name], 0, task_interval)
		
## Run the task_init function for each loaded task.
def init_tasks():
	for task_name, task_info in tasks.items():
		task_module, task_time, task_interval = task_info
		
		log("TASK", "Starting up [" + task_name + "]")
		libsigma.safe_mode(task_module.task_init)
		tasks[task_name] = (task_module, time.time(), task_interval)

## Run the task_execute function for each task whose delay period has passed.
def run_tasks():
	for task_name, task_info in tasks.items():
		task_module, task_time, task_interval = task_info
		
		if time.time() >= (task_time + task_interval):
			libsigma.safe_mode(task_module.task_execute)
			tasks[task_name] = (task_module, time.time(), task_interval)

## Run the task_deinit function for each task upon server shutdown.
def deinit_tasks():
	for task_name, task_info in tasks.items():
		task_module, task_time, task_interval = task_info
		
		log("TASK", "Shutting down [" + task_name + "]")
		libsigma.safe_mode(task_module.task_deinit)
