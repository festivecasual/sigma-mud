import sys
from xml.dom import pulldom
from xml.sax import SAXParseException
import handler, world
from common import *

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
					world.rooms[ref] = world.room()
	except SAXParseException, msg:
		log("FATAL", "XML Error: " + str(msg))
		sys.exit(1)

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
					handler.mappings[command] = handler.functions[function]
	except SAXParseException, msg:
		log("FATAL", "XML Error: " + str(msg))
		sys.exit(1)
