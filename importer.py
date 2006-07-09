import sys
from xml.dom import pulldom
from xml.sax import SAXParseException
from common import *

def process_xml():
	try:
		server_xml = open(options["xml_root"] + "/server.xml")
	except IOError:
		log("FATAL", "Unable to open " + options["xml_root"] + "/server.xml")
		sys.exit(1)

	try:
		events = pulldom.parse(server_xml)
		for (event, node) in events:
			if event == pulldom.START_ELEMENT:
				log("Yep", "Yep")
	except SAXParseException, msg:
		log("FATAL", "XML parsing error: " + str(msg))
		sys.exit(1)
