import asyncore, glob, os.path, imp, sys
import network
from common import *

def main():
	log("SYSTEM", "Startup in progress")

	log("MODULES", "Loading task modules")
	task_modules = glob.glob("./tasks/*.py")
	for task_file in task_modules:
		source = os.path.basename(task_file)
		name = os.path.splitext(source)[0]
		try:
			imp.load_source(name, "./tasks/" + source)
			sys.modules[name].task_init()
			log("TASK", "Task [" + sys.modules[name].task_info()[0] + "] loaded successfully")
		except:
			log("ERROR", "Task [" + source + "] broken, change .py extention to disable")

	log("NETWORK", "Initializing master socket")
	listener = network.server_socket()

	log("SYSTEM", "Startup complete, entering main loop")

	while True:
		try:
			asyncore.loop(timeout=0.1, count=1)
		except KeyboardInterrupt:
			log("INPUT", "Interrupt detected")
			break

	log("SYSTEM", "Shutdown in progress")

	# ...

	log("SYSTEM", "Shutdown complete")


if __name__ == "__main__":
	main()
