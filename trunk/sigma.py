## @package sigma
#  Start the Sigma server and initialize the main control loop.

## @mainpage
#  This documentation contains descriptions of all class structures and modules
#  contained within Sigma.

import asyncore
import command, handler, importer, network, order, task, world
from common import *

## The primary control function for Sigma.
def main():
	log("SYSTEM", "Startup in progress")

	log("MODULES", "Inspecting task modules")
	task.load_tasks()

	log("MODULES", "Inspecting handler modules")
	handler.load_handlers()
	
	log("ORDERS", "Inspecting order modules")
	order.load_orders()

	log("XML", "Processing server.xml")
	importer.process_xml()

	log("WORLD", "Resolving location linkages")
	world.resolve_links()
	
	log("WORLD", "Resolving populator objects")
	world.resolve_populators()
	
	log("WORLD", "Resolving placement objects")
	world.resolve_placements()

	log("NETWORK", "Initializing master socket")
	listener = network.server_socket()
	
	log("TASK", "Initializing task modules")
	task.init_tasks()

	log("SYSTEM", "Startup complete, entering main loop")
	while True:
		try:
			asyncore.loop(timeout=0.1, count=1)
			command.process_commands()
			task.run_tasks()
		except KeyboardInterrupt:
			print("")
			log("CONSOLE", "Keyboard interrupt detected")
			break

	log("SYSTEM", "Shutdown in progress")

	log("NETWORK", "Shutting down master socket")
	listener.close()

	log("MODULES", "Deinitializing task modules")
	task.deinit_tasks()

	log("SYSTEM", "Shutdown complete")


if __name__ == "__main__":
	main()
