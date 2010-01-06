import glob
import os.path
import imp
import sys
import time

import libsigma
from common import *


tasks = {}


def load_tasks():
    task_modules = glob.glob(os.path.join(directories["tasks_root"], "*.py"))
    for task_file in task_modules:
        source = os.path.basename(task_file)
        module_name = "task_" + os.path.splitext(source)[0]

        try:
            imp.load_source(module_name, os.path.join(directories["tasks_root"], source))

            task_name = sys.modules[module_name].name
            task_interval = sys.modules[module_name].interval

            f_init = sys.modules[module_name].task_init
            f_execute = sys.modules[module_name].task_execute
            f_deinit = sys.modules[module_name].task_deinit
        except:
            log("  *  ERROR", "Task module [" + source + "] is not functional")
            continue

        log("TASK", "Loading task [" + task_name + "]")
        tasks[task_name] = (sys.modules[module_name], 0, task_interval, -1)


def init_tasks():
    for task_name, task_info in tasks.items():
        task_module, task_time, task_interval, task_ttl = task_info

        log("TASK", "Starting up [" + task_name + "]")
        libsigma.safe_mode(task_module.task_init)
        tasks[task_name] = (task_module, time.time(), task_interval, task_ttl)


def run_tasks():
    for task_name, task_info in tasks.items():
        task_module, task_time, task_interval, task_ttl = task_info

        if time.time() >= (task_time + task_interval):
            libsigma.safe_mode(task_module.task_execute)
            if task_ttl > 1:
                tasks[task_name] = (task_module, time.time(), task_interval, task_ttl - 1)
            elif task_ttl == 1:
                del tasks[task_name]
            else:
                tasks[task_name] = (task_module, time.time(), task_interval, -1)


def deinit_tasks():
    for task_name, task_info in tasks.items():
        task_module, task_time, task_interval, task_ttl = task_info

        log("TASK", "Shutting down [" + task_name + "]")
        libsigma.safe_mode(task_module.task_deinit)
