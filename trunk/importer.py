## @package importer
#  Pull in data from XML configuration files.

import sys, pickle
from xml.dom import pulldom
from xml.sax import SAXParseException
import handler, world, creation
from common import *

## Main function for processing server.xml and subordinate files.
def process_xml():
	try:
		server_xml = open(directories["xml_root"] + "/server.xml")
	except IOError:
		log("FATAL", "Unable to open " + directories["xml_root"] + "/server.xml")
		sys.exit(1)

	try:
		events = pulldom.parse(server_xml)
		for (event, node) in events:
			if event == pulldom.START_ELEMENT:
				if node.tagName == "option":
					if (not node.attributes.has_key("name")) or (not node.attributes.has_key("value")):
						log("FATAL", "Error in <option /> tag")
						sys.exit(1)
					if not options.has_key(node.attributes["name"].value):
						log("FATAL", "<option /> tag sets unknown option")
						sys.exit(1)
					options[node.attributes["name"].value] = node.attributes["value"].value
					log("CONFIG", "Option [" + node.attributes["name"].value + "] set to '" + node.attributes["value"].value + "'")
				elif node.tagName == "area":
					if (not node.attributes.has_key("file")) or (not node.attributes.has_key("name")):
						log("FATAL", "Error in <area /> tag")
						sys.exit(1)
					try:
						area_xml = open(directories["xml_root"] + "/" + node.attributes["file"].value)
					except IOError:
						log("FATAL", "Unable to open area XML source [" + node.attributes["file"].value)
						sys.exit(1)
					log("XML", "Processing area file at [" + node.attributes["file"].value + "]")
					process_area(area_xml, node.attributes["name"].value)
					area_xml.close()
				elif node.tagName == "calendar":
					if (not node.attributes.has_key("file")) or (not node.attributes.has_key("name")):
						log("FATAL", "Error in <calendar /> tag")
						sys.exit(1)
					try:
						calendar_xml = open(directories["xml_root"] + "/" + node.attributes["file"].value)
					except IOError:
						log("FATAL", "Unable to open area XML source [" + node.attributes["file"].value)
						sys.exit(1)
					log("XML", "Processing calendar file at [" + node.attributes["file"].value + "]")
					process_calendar(calendar_xml, node.attributes["name"].value) 
				   	calendar_xml.close()
				elif node.tagName == "class":
					if not node.attributes.has_key("file"):
						log("FATAL", "Error in <class /> tag")
						sys.exit(1)
					try:
						class_xml = open(directories["xml_root"] + "/" + node.attributes["file"].value)
					except IOError:
						log("FATAL", "Unable to open class XML source [" + node.attributes["file"].value + "]")
						sys.exit(1)
					log("XML", "Processing class definition at [" + node.attributes["file"].value + "]")
					process_class(class_xml)
					class_xml.close()
				elif node.tagName == "handlers":
					if not node.attributes.has_key("file"):
						log("FATAL", "Error in <handlers /> tag")
						sys.exit(1)
					try:
						handlers_xml = open(directories["xml_root"] + "/" + node.attributes["file"].value)
					except IOError:
						log("FATAL", "Unable to open handlers XML source [" + node.attributes["file"].value + "]")
						sys.exit(1)
					log("XML", "Processing handler mappings in [" + node.attributes["file"].value + "]")
					process_handlers(handlers_xml)
					handlers_xml.close()

	except SAXParseException, msg:
		log("FATAL", "XML Error: " + str(msg))
		sys.exit(1)

	server_xml.close()

## Traverse an area definition and create all necessary world objects.
#
#  @param f The area node to process.
#  @param name The name of the area (used to dereference links).
def process_area(f, name):
	try:
		events = pulldom.parse(f)
		for (event, node) in events:
			if event == pulldom.START_ELEMENT:
				if node.tagName == "room":
					if not node.attributes.has_key("id"):
						log("FATAL", "Error in <room> tag")
						sys.exit(1)

					ref = name + ":" + node.attributes["id"].value

					events.expandNode(node)
					world.rooms[ref] = world.room(ref, node)

				elif node.tagName == "denizen":
					if not node.attributes.has_key("id"):
						log("FATAL", "Error in <denizen> tag")
						sys.exit(1)

					ref = name + ":" + node.attributes["id"].value

					events.expandNode(node)
					world.denizens_source[ref] = pickle.dumps(world.denizen(node))
				
				elif node.tagName == "item":
					if not node.attributes.has_key("id"):
						log("FATAL", "Error in <item> tag")
						sys.exit(1)
					
					ref = name + ":"+ node.attributes["id"].value
					
					events.expandNode(node)
					world.items_source[ref] = pickle.dumps(world.item(node))
				
				elif node.tagName == "populator":
					if not node.attributes.has_key("denizen") or not node.attributes.has_key("target"):
						log("FATAL", "Error in <populator> tag")
						sys.exit(1)
					
					events.expandNode(node)
					world.populators.append(world.populator(node, name))
				
				elif node.tagName == "placement":
					if not node.attributes.has_key("item") or not node.attributes.has_key("target"):
						log("FATAL", "Error in <placement> tag")
						sys.exit(1)
					
					events.expandNode(node)
					world.placements.append(world.placement(node, name))

	except SAXParseException, msg:
		log("FATAL", "XML Error: " + str(msg))
		sys.exit(1)

## Traverse a handler definition structure and create mappings.
#
#  @param f The handler node to process.
def process_handlers(f):
	try:
		events = pulldom.parse(f)
		for (event, node) in events:
			if event == pulldom.START_ELEMENT:
				if node.tagName == "handler":
					if (not node.attributes.has_key("command")) or (not node.attributes.has_key("function")):
						log("FATAL", "Error in <handler /> tag")
						sys.exit(1)
					command = node.attributes["command"].value
					function = node.attributes["function"].value
					if not handler.functions.has_key(function):
						log("FATAL", "Handler maps non-existent function to command <" + command + ">")
						sys.exit(1)
					handler.mappings.append((command, handler.functions[function]))
				if node.tagName == "special":
					if (not node.attributes.has_key("type")) or (not node.attributes.has_key("rewrite")):
						log("FATAL", "Error in <special /> tag")
						sys.exit(1)
					special_type = node.attributes["type"].value
					rewrite = node.attributes["rewrite"].value
					if not special_type in handler.specials.keys():
						log("FATAL", "Special handler tag references unsupported type <" + special_type + ">")
						sys.exit(1)
					handler.specials[special_type] = rewrite.encode('ascii')
	except SAXParseException, msg:
		log("FATAL", "XML Error: " + str(msg))
		sys.exit(1)

def process_calendar(f, name):
	events = pulldom.parse(f)
	for (event, node) in events:
		if event == pulldom.START_ELEMENT:
			if node.tagName == "calendar":
				if not node.attributes.has_key("name"):
					log("FATAL", "Error in <calendar> tag")
					sys.exit(1)

				ref=node.attributes["name"].value
				events.expandNode(node)
				world.calendars.append(world.calendar(ref, node))

def process_class(f):
	events = pulldom.parse(f)
	for (event, node) in events:
		if event == pulldom.START_ELEMENT:
			if node.tagName == "class":
				events.expandNode(node)
				new_class = creation.character_class(node)
				creation.classes[new_class.name] = new_class

