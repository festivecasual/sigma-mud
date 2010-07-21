import pickle
import os.path
from xml.etree import ElementTree

import handler
import world
import creation
import feats
from common import *


def process_xml():
    try:
        server_path = os.path.join(directories["xml_root"], "server.xml")
        server_xml = ElementTree.parse(server_path).getroot()
    except:
        log("FATAL", "Unable to open and parse server.xml: %s" % server_path, exit_code=1)

    for option in server_xml.findall('option'):
        name = required_attribute(option, 'name')
        value = required_attribute(option, 'value')
        if not options.has_key(name):
            log("FATAL", "<option> tag sets unknown option %s" % name, exit_code=1)
        options[name] = value
        log("CONFIG", "Option [%s] set to '%s'" % (name, value))
        server_xml.remove(option)

    for s in server_xml.findall('stance'):
        file = required_attribute(s, 'file')
        log("STANCE", "Processing stances at %s" % (file))
        try:
            stance_path=os.path.join(directories["xml_root"], file)
            stance_xml= ElementTree.parse(stance_path).getroot()
        except:
            log("FATAL", "Unable to parse stance file", exit_code=1)
        process_stance(stance_xml)
        server_xml.remove(s)

    for area in server_xml.findall('area'):
        file = required_attribute(area, 'file')
        name = required_attribute(area, 'name')
        log("AREA", "Processing area [%s] at %s" % (name, file))
        try:
            area_path = os.path.join(directories["xml_root"], file)
            area_xml = ElementTree.parse(area_path).getroot()
        except:
            log("FATAL", "Unable to parse area file", exit_code=1)
        process_area(area_xml, name)
        server_xml.remove(area)

    for calendar in server_xml.findall('calendar'):
        file = required_attribute(calendar, 'file')
        name = required_attribute(calendar, 'name')
        log("CALENDAR", "Processing calendar [%s] at %s" % (name, file))
        try:
            calendar_path = os.path.join(directories["xml_root"], file)
            calendar_xml = ElementTree.parse(calendar_path).getroot()
        except:
            log("FATAL", "Unable to parse calendar file", exit_code=1)
        world.calendars.append(world.calendar(calendar_xml, name))
        server_xml.remove(calendar)
              
    for cclass in server_xml.findall('class'):
        file = required_attribute(cclass, 'file')
        log("CLASS", "Processing class definition at %s" % file)
        try:
            cclass_path = os.path.join(directories["xml_root"], file)
            cclass_xml = ElementTree.parse(cclass_path).getroot()
        except:
            log("FATAL", "Unable to parse class definition", exit_code=1)
        process_class(cclass_xml)
        server_xml.remove(cclass)

    for handlers in server_xml.findall('handlers'):
        file = required_attribute(handlers, 'file')
        log("HANDLERS", "Processing handlers mapping at %s" % file)
        try:
            handlers_path = os.path.join(directories["xml_root"], file)
            handlers_xml = ElementTree.parse(handlers_path).getroot()
        except:
            log("FATAL", "Unable to parse handler mapping", exit_code=1)
        process_handlers(handlers_xml)
        server_xml.remove(handlers)

    for child in server_xml.getchildren():
        log("ERROR", "Ignoring unknown tag <%s> in server.xml" % child.tag, problem=True)


def process_area(area_xml, area_name):
    for room in area_xml.findall('room'):
        id = required_attribute(room, 'id')
        ref = '%s:%s' % (area_name, id)
        world.rooms[ref] = world.room(ref, room)
        area_xml.remove(room)

    for denizen in area_xml.findall('denizen'):
        id = required_attribute(denizen, 'id')
        ref = '%s:%s' % (area_name, id)
        world.denizens_source[ref] = pickle.dumps(world.denizen(denizen))
        area_xml.remove(denizen)

    for item in area_xml.findall('item'):
        id = required_attribute(item, 'id')
        ref = '%s:%s' % (area_name, id)
        world.items_source[ref] = pickle.dumps(world.item(item))
        area_xml.remove(item)

    for door in area_xml.findall('door'):
        world.doors.append(world.door(door, area_name, len(world.doors)))
        area_xml.remove(door)

    for populator in area_xml.findall('populator'):
        denizen = required_attribute(populator, 'denizen')
        target = required_attribute(populator, 'target')
        world.populators.append(world.populator(populator, area_name, denizen, target))
        area_xml.remove(populator)

    for placement in area_xml.findall('placement'):
        item = required_attribute(placement, 'item')
        target = required_attribute(placement, 'target')
        q = placement.get('quantity')
        quantity = 1 if not q else q
        world.placements.append(world.placement(placement, area_name, item, target, quantity))
        area_xml.remove(placement)

    for child in area_xml.getchildren():
        log('ERROR', 'Ignoring unknown tag <%s> in area file [%s]' % (child.tag, area_name), problem=True)


def process_handlers(handlers_xml):
    for handler_item in handlers_xml.findall('handler'):
        command = required_attribute(handler_item, 'command')
        function = required_attribute(handler_item, 'function')
        if not handler.functions.has_key(function):
            log('FATAL', 'Handler maps non-existent function <%s> to command <%s>' % (function, command), exit_code=1)
        handler.mappings.append((command, handler.functions[function]))

    for special in handlers_xml.findall('special'):
        special_type = required_attribute(special, 'type')
        rewrite = required_attribute(special, 'rewrite')
        if not special_type in handler.specials.keys():
            log('FATAL', 'Special handler tag references unsupported type <%s>' % special_type, exit_code=1)
        handler.specials[special_type] = rewrite.encode('ascii')


def process_class(class_xml):
    for pclass_xml in class_xml.findall('class'):
        new_class = creation.character_class(pclass_xml)
        creation.classes[new_class.name] = new_class
        
def process_stance(stance_xml):
    for instance in stance_xml.findall('stance'):
        new_stance=feats.stance(instance)
        log ('STANCE', 'Added new stance "%s"' %new_stance.name)
        feats.stances[new_stance.name]=new_stance
        if new_stance.default:
            feats.default_stances.append(new_stance)