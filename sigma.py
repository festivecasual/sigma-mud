import asyncore
import network, command, task
from common import *

def main():
	log("SYSTEM", "Startup in progress")

	log("MODULES", "Loading task modules")
	task.load_tasks()

	log("NETWORK", "Initializing master socket")
	listener = network.server_socket()

	log("SYSTEM", "Startup complete, entering main loop")

	while True:
		try:
			asyncore.loop(timeout=0.1, count=1)
			command.process_commands()
			task.run_tasks()
		except KeyboardInterrupt:
			log("CONSOLE", "Keyboard interrupt detected")
			break

	log("SYSTEM", "Shutdown in progress")

	log("MODULES", "Deinitializing task modules")
	task.deinit_tasks()

	log("SYSTEM", "Shutdown complete")


if __name__ == "__main__":
	main()
