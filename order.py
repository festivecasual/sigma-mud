## @package order
#  Defines the character order framework.

## @defgroup order Built-In Orders
#  Orders included as default infrastructure within the environment.
#
#  @sa The order framework is defined in order.py.

import glob, os.path, imp, sys
from common import *

## Holds all available character orders
orders = {}

## Process the orders/ directory and load orders into master order list.
def load_orders():
	order_modules = glob.glob(directories["orders_root"] + "/*.py")
	for order_file in order_modules:
		source = os.path.basename(order_file)
		module_name = "order_" + os.path.splitext(source)[0]

		try:
			imp.load_source(module_name, directories["orders_root"] + "/" + source)

			order_name = sys.modules[module_name].name
		except:
			log("  *  ERROR", "Order module [" + source + "] is not functional")
			continue

		log("ORDER", "Loading order [" + order_name + "]")
		orders[order_name] = sys.modules[module_name]