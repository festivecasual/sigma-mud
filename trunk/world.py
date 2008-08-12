## @package world
#  Contains data structures for objects and constructs within the environment.

import sys, libsigma
from common import *

## All players currently in game.
players = []

## All available rooms (mapped to area:name).
rooms = {}

## All denizens active in the game.
denizens = {}

## All items active in the game.
items = {}


## Denizen prototypes (for pickle).
denizens_source = {}

## Item prototypes (for pickle).
items_source = {}

## All populator objects (for placing denizens in rooms).
populators = []

## All placement objects (for placing items in game).
placements = []

#All Calendars in the game
calendars = []

## Map exit codes to room objects, reporting any mapping errors.
def resolve_links():
	for current in rooms.values():		
		for i in range(NUM_DIRS):
			if not current.exits[i]:
				continue

			if rooms.has_key(current.exits[i]):
				current.exits[i] = rooms[current.exits[i]]
			elif rooms.has_key(current.area + ":" + current.exits[i]):
				current.exits[i] = rooms[current.area + ":" + current.exits[i]]
			else:
				log("  *  ERROR", "Unresolved room exit linkage: " + current.exits[i] + " (" + current.location + ")")
				current.exits[i] = None

## Map populator references to template denizens, reporting any mapping errors.
def resolve_populators():
	for current in populators:
		if denizens_source.has_key(current.denizen):
			current.denizen = denizens_source[current.denizen]
		elif denizens_source.has_key(current.area + ":" + current.denizen):
			current.denizen = denizens_source[current.area + ":" + current.denizen]
		else:
			log("  *  ERROR", "Unresolved denizen reference: " + current.denizen)
		
		if rooms.has_key(current.target):
			current.target = rooms[current.target]
		elif rooms.has_key(current.area + ":" + current.target):
			current.target = rooms[current.area + ":" + current.target]
		else:
			log("  *  ERROR", "Unresolved target room reference: " + current.target)

## Map placement references to template items, reporting any mapping errors.
def resolve_placements():
	for current in placements:
		if items_source.has_key(current.item):
			current.item = items_source[current.item]
		elif items_source.has_key(current.area + ":" + current.item):
			current.item = items_source[current.area + ":" + current.item]
		else:
			log("  *  ERROR", "Unresolved denizen reference: " + current.item)
		
		if rooms.has_key(current.target):
			current.target = rooms[current.target]
		elif rooms.has_key(current.area + ":" + current.target):
			current.target = rooms[current.area + ":" + current.target]
		else:
			log("  *  ERROR", "Unresolved target room reference: " + current.target)

## Encapsulates an instruction to place a denizen in a certain location.
class populator(object):
	## Construct the populator object.
	#
	#  @param self The active instance.
	#  @param node The XML node describing the populator.
	#  @param area The name of the populator's area (for mapping).
	def __init__(self, node, area):
		## The denizen template to load.
		self.denizen = node.attributes["denizen"].value
		
		## The destination room.
		self.target = node.attributes["target"].value
		
		## The area containing the populator.
		self.area = area
		
		## Any option flags applicable to the populator.
		self.flags = []
		
		## Cache value to track the current instantiated denizen.
		self.instance = None
		
		node.normalize()
		for info_node in node.childNodes:
			if info_node.nodeName == "flag":
				self.flags.append(strip_whitespace(info_node.firstChild.data))

## Encapsulates an instruction to place an item in a certain location.
class placement(object):
	## Construct the placement object.
	#
	#  @param self The active instance.
	#  @param node The XML node describing the placement.
	#  @param area The name of the placement's area (for mapping).
	def __init__(self, node, area):
		## The item template to load.
		self.item = node.attributes["item"].value
		
		## The destination room or object.
		self.target = node.attributes["target"].value
		
		## The area containing the placement.
		self.area = area
		
		## Any option flags applicable to the placement.
		self.flags = []
		
		## Cache value to track the current instantiated item.
		self.instance = None
		
		node.normalize()
		for info_node in node.childNodes:
			if info_node.nodeName == "flag":
				self.flags.append(strip_whitespace(info_node.firstChild.data))

## Encapsulates any entity within the world structure.
class entity(object):
	## Construct the basic default entity.
	#
	#  @param self The active instance.
	def __init__(self):
		## The name of the entity.
		self.name = ""
		
		## The long description of the entity.
		self.desc = ""
		
		## Keywords applicable when searching for the entity.
		self.keywords = []
		
		## Contents of the entity.
		self.contents = []
		
		## Capacity of the entity to hold contents.
		self.capacity = 0
		
		## The entity's room location.
		self.location = ""

## Encapsulates a tangible object within the world.
class item(entity):
  ## Construct the item from XML.
  #
  #  @param self The active instance.
  #  @param node The XML node describing the item.
  def __init__(self, node):
    entity.__init__(self)
    
    node.normalize()
    for info_node in node.childNodes:
   		if info_node.nodeName == "name":
			self.name = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
		elif info_node.nodeName == "keywords":
			self.keywords.extend(strip_whitespace(info_node.firstChild.data).lower().split())
		elif info_node.nodeName == "short":
			## The short description of the item.
			self.short = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
		elif info_node.nodeName == "desc":
			self.desc = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))

## Encapsulates a room within the world.
class room(entity):
	## Construct the room from XML.
	#
	#  @param self The active instance.
	#  @param ref The reference code for the room.
	#  @param node The XML node describing the room.
	def __init__(self, ref, node):
		entity.__init__(self)
		self.location = ref
		
		## The characters (denizens and players) occupying the room.
		self.characters = []

		self.keywords = ["room"]
		
		## List of all exits, ultimately resolved to other room objects.
		self.exits = [None] * NUM_DIRS
		
		## Mapping of points of interest within the room.
		self.foci = {}
		
		self.capacity = -1

		node.normalize()
		for info_node in node.childNodes:
			if info_node.nodeName == "name":
				self.name = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "desc":
				self.desc = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "focus":
				if not info_node.attributes.has_key("name"):
					log("FATAL", "Error in <focus /> tag within <room />")
					sys.exit(1)
				name = info_node.attributes["name"].value
				description = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
				
				self.foci[name] = description
			elif info_node.nodeName == "exit":
				if (not info_node.attributes.has_key("dir")) or (not info_node.attributes.has_key("target")):
					log("FATAL", "Error in <room /> tag")
					sys.exit(1)
				dir = libsigma.txt2dir(info_node.attributes["dir"].value)
				if dir == -1:
					log("FATAL", "Bad exit direction: " + info_node.attributes["dir"].value)
					sys.exit(1)
				self.exits[dir] = info_node.attributes["target"].value

	## Return the area portion of the room's location code.
	#
	#  @param self The active instance.
	def get_area(self):
		return self.location[:self.location.find(":")]

	## Provide a property structure to return the room's area.
	area = property(get_area)

## Encapsulates an abstract denizen or player within the world.
class character(entity):
	## Construct the abstract character.
	#
	#  @param self The active instance.
	def __init__(self):
		entity.__init__(self)
		
		## States defined in common module, determines processing context of input.
		self.state = STATE_NULL

	## Abstract function to simulate sending a prompt string to a player.
	#
	#  @param self The active instance.
	def send_prompt(self): pass

	## Abstract function to send data to the character.
	#
	#  @param self The active instance.
	#  @param s The data to send.
	def send(self, s = ""): pass

	## Abstract convenience function to send a line of data to the character.
	#
	#  @param self The active instance.
	#  @param s The data to send.
	#  @param breaks The number of breaks to send, following \c s.
	def send_line(self, s = "", breaks = 1): pass

## Encapsulates a denizen (non-playing character) within the world.
class denizen(character):
	## Construct the denizen.
	#
	#  @param self The active instance.
	#  @param node The XML node describing the denizen.
	def __init__(self, node):
		character.__init__(self)

		self.state = STATE_PLAYING
		
		node.normalize()
		for info_node in node.childNodes:
			if info_node.nodeName == "name":
				self.name = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "keywords":
				self.keywords.extend(strip_whitespace(info_node.firstChild.data).lower().split())
			elif info_node.nodeName == "short":
				## The short description of the denizen.
				self.short = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))
			elif info_node.nodeName == "desc":
				self.desc = wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"]))

## Encapsulates a player (with a socket connection) within the world.
class player(character):
	## Construct the player.
	#
	#  @param self The active instance.
	#  @param s The player's socket object.
	def __init__(self, s):
		character.__init__(self)
		
		## Holds savegame data from archive.
		self.proto = None
		
		## Holds player password.
		self.password = None
		
		## Holds the client socket for the player.
		self.socket = None
		self.state = STATE_INIT

		self.socket = s
		self.send_prompt()
	
	## Send a prompt to the player.
	#
	#  @param self The active instance.
	def send_prompt(self):
		self.socket.push(prompts[self.state])

		if (self.state == STATE_INIT):
			self.state = STATE_NAME
			self.send_prompt()

	## Send data to the player.
	#
	#  @param self The active instance.
	#  @param s The data to send.
	def send(self, s = ""):
		self.socket.push(s)

	## Convenience function to send a line of data to the player.
	#
	#  @param self The active instance.
	#  @param s The data to send.
	#  @param breaks The number of breaks to send, following \c s.
	def send_line(self, s = "", breaks = 1):
		self.send(s)
		self.send("\r\n" * breaks)

	## Overloaded function to return search keywords for the player.
	#
	#  @param self The active instance.
	def get_keywords(self):
		return [self.name.lower()]
	
	## Blank function to complete the property() assignment to keywords.
	#
	#  @param self The active instance.
	#  @param data (Not processed) the provided data.
	def set_keywords(self, data):
		pass
	
	keywords = property(get_keywords, set_keywords)
	
	## Returns a short description of the player.
	#
	#  @param self The active instance.
	def get_short(self):
		return self.name + " is here."
	
	## The short description of the player (using player name).
	short = property(get_short)

class calendar(object):
    ## Construct a calendar from xml
	#
	#  @param self The active instance.
	#  @param ref The reference code for the room.
	#  @param node The XML node describing the room.
    def __init__(self,cname, node):
    	self.name=cname
    	self.daylength=0 # measured in RL hours
    	self.yearlength=0 # measured in IG Days
    	self.months={}
    	self.monthlist= []
    	self.holidays={}
    	self.watershed_name=""
    	self.watershed_date=""
     	node.normalize()
     	## Bunch of calendar compliance checks below
    	for info_node in node.childNodes:
			if info_node.nodeName == "IGDayLengthInHours":
				try:
					self.daylength = int(wordwrap(strip_whitespace(info_node.firstChild.data), int(options["wrap_size"])))
				except ValueError:
					log("FATAL", "IGDayLengthInHours property must be an integer")
					sys.exit(1)
				if(self.daylength < 1 or self.daylength > 24):
					log("FATAL", "IGDayLengthInHours property must be between 1 and 24 inclusive")
					sys.exit(1)
			elif info_node.nodeName== "month":
				if (not info_node.attributes.has_key("name")) or (not info_node.attributes.has_key("days")):
					log("FATAL", "Error in <month /> tag")
					sys.exit(1)
				if(self.months.has_key(info_node.attributes["name"].value)):
				   	log("FATAL", "Duplicate month name found. Month names must be unique")
				   	sys.exit(1)
				try:
					self.months[info_node.attributes["name"].value]=int(info_node.attributes["days"].value)
					self.monthlist.append(info_node.attributes["name"].value)
				except ValueError:
					log("FATAL", "days property must be an integer")
					sys.exit(1)
				if(self.months[info_node.attributes["name"].value] < 1):
					log("FATAL", "days must be greater than 0")
					sys.exit(1)		
			elif info_node.nodeName=="holiday":
				holiday_compliance=True
				if (not info_node.attributes.has_key("name")) or (not info_node.attributes.has_key("month_day")) or (not info_node.attributes.has_key("month")):
					log("FATAL", "Error in <holiday /> tag")
					sys.exit(1)
				if(self.holidays.has_key(info_node.attributes["name"].value)):
				   	log("FATAL", "Duplicate holiday name found. Holiday names must be unique")
				   	sys.exit(1)
				try:
					int(info_node.attributes["month_day"].value)
				except ValueError:
					log("FATAL", "month_day property must be an integer")
					sys.exit(1)
				if(not self.months.has_key(info_node.attributes["month"].value)):
					holiday_compliance=False
				else:
					if(int(info_node.attributes["month_day"].value) > self.months[info_node.attributes["month"].value] or int(info_node.attributes["month_day"].value) < 1):
						   holiday_compliance=False
					
				if(holiday_compliance):
					self.holidays[info_node.attributes["name"].value]={info_node.attributes["month"].value:int(info_node.attributes["month_day"].value)}
				else:
					log("ERROR", "Cannot create " + info_node.attributes["name"].value + " holiday")
			elif info_node.nodeName=="WatershedEvent": ## TODO add Compliance to Watershed Event values
				if(not info_node.attributes.has_key("title") or not info_node.attributes.has_key("date")  ):
					log("FATAL", "Error in <Watershed Event /> tag")
					sys.exit(1)
				self.watershed_name=info_node.attributes["title"].value
				self.watershed_date=info_node.attributes["date"].value  + " 00:00:00"
    	for m in self.months:
    		self.yearlength+=self.months[m]
    
    	
    def get_current_IG_DateTime(self):
    	current_time=""
    	current_time=date_time_string()
    	c_y,c_m,c_d,c_h,c_M,c_s=self.unpackDate(current_time)
    	z_y,z_m,z_d,z_h,z_M,z_s=self.unpackDate(self.watershed_date)
    	#current_date_list=self.unpackDate(current_time)
     	#zero_date_list=self.unpackDate(self.watershed_date)
     	
    	current_date=datetime.datetime(int(c_y),int(c_m),int(c_d),int(c_h),int(c_M),int(c_s))
    	zero_date=datetime.datetime(int(z_y),int(z_m),int(z_d),int(z_h),int(z_M),int(z_s))
    	#current_date=datetime.datetime(*current_date_list)
    	#zero_date=datetime.datetime(*zero_date)
    	date_diff=current_date-zero_date;
    	
    	##hours rollup
    	hours=date_diff.seconds/3600
    	remainder=date_diff.seconds%3600
    	minutes=int(remainder/60)
    	seconds=remainder%60
    	IG_days_diff=date_diff.days*24/self.daylength + int(hours/self.daylength)
    	hours=hours%self.daylength
    	
      	IGyear=IG_days_diff/self.yearlength;
      	IGdays_remainder=IG_days_diff%self.yearlength
      	
      	for month in self.monthlist:
      		if(IGdays_remainder>self.months[month]):
      		 	IGdays_remainder-=int(self.months[month])
      		else:
      			IGmonth=month
      			IGday=IGdays_remainder
      			break
     
        return "It is the " + ordinals(IGday) + " of " + str(IGmonth) + ", " + str(IGyear) + " years since the " + self.watershed_name + "." 
    # returns list in format [month, day, year, hours, mins, seconds]
    def unpackDate(self, date):
    	t_date=date.replace(" ", "/")
    	t_date=t_date.replace(":", "/")
    	sp = t_date.split("/")
    	for x in sp:
    	  x=int(x)		
    	return sp;
	  
	   	
				