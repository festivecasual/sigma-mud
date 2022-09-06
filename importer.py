import os.path
from xml.etree import ElementTree

import handler
import creation
import feats
from calendar import Calendar
from magic import Spell
from world import World, Room, Door, Populator, Placement
from entities import Item, Denizen
from common import *


def process_xml():
    try:
        server_path = os.path.join(directories["xml_root"], "server.xml")
        server_xml = ElementTree.parse(server_path).getroot()
    except:
        log("FATAL", "Unable to open and parse server.xml: %s" % server_path, exit_code=1)

    w = World()

    for option in server_xml.findall('option'):
        name = required_attribute(option, 'name')
        value = required_attribute(option, 'value')
        if name not in options:
            log("FATAL", "<option> tag sets unknown option %s" % name, exit_code=1)
        options[name] = value
        log("CONFIG", "Option [%s] set to '%s'" % (name, value))
        server_xml.remove(option)

    for s in server_xml.findall('stance'):
        file = required_attribute(s, 'file')
        log("STANCE", "Processing stances at %s" % file)
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

        w.calendars.append(Calendar(calendar_xml, name))
        server_xml.remove(calendar)

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

    for spells in server_xml.findall('spells'):
        file = required_attribute(spells, 'file')
        log("MAGIC", "Processing spells mapping at %s" % file)
        try:
            spell_path = os.path.join(directories["xml_root"], file)
            spells_xml = ElementTree.parse(spell_path).getroot()
            spells_package=required_attribute(spells_xml,'package')
            spells_package=spells_package.split('.')
        except:
            log("FATAL", "Unable to parse spell file: %s" % file, exit_code=1)
        for spell in spells_xml.findall('spell'):
            m = __import__(SPELL_PACKAGE + '.' + spells_package[0])
            classname = required_attribute(spell,'class')
            for package in spells_package:
                m=getattr(m,package)
            spell_class=getattr(m, classname)
            new_spell=spell_class(spell)
            feats.spells[new_spell.name]=new_spell
            log("MAGIC","Added spell [%s] to game" % new_spell.name)
        server_xml.remove(spells)
    
    for child in server_xml.getchildren():
        log("ERROR", "Ignoring unknown tag <%s> in server.xml" % child.tag, problem=True)


def process_area(area_xml, area_name):
    w = World()

    for room in area_xml.findall('room'):
        id = required_attribute(room, 'id')
        ref = '%s:%s' % (area_name, id)
        w.rooms[ref] = Room(ref, room)
        area_xml.remove(room)

    for denizen in area_xml.findall('denizen'):
        id = required_attribute(denizen, 'id')
        ref = '%s:%s' % (area_name, id)
        w.denizens_source[ref] = denizen
        area_xml.remove(denizen)

    for item in area_xml.findall('item'):
        id = required_attribute(item, 'id')
        ref = '%s:%s' % (area_name, id)
        w.items_source[ref] = item
        area_xml.remove(item)

    for door in area_xml.findall('door'):
        w.doors.append(Door(door, area_name))
        area_xml.remove(door)

    for populator in area_xml.findall('populator'):
        denizen = required_attribute(populator, 'denizen')
        target = required_attribute(populator, 'target')
        w.populators.append(Populator(populator, area_name, denizen, target))
        area_xml.remove(populator)

    for placement in area_xml.findall('placement'):
        item = required_attribute(placement, 'item')
        target = required_attribute(placement, 'target')
        q = placement.get('quantity')
        quantity = 1 if not q else q
        w.placements.append(Placement(placement, area_name, item, target, quantity))
        area_xml.remove(placement)

    for child in area_xml.getchildren():
        log('ERROR', 'Ignoring unknown tag <%s> in area file [%s]' % (child.tag, area_name), problem=True)


def process_handlers(handlers_xml):
    for handler_item in handlers_xml.findall('handler'):
        command = required_attribute(handler_item, 'command')
        function = required_attribute(handler_item, 'function')
        if function not in handler.functions:
            log('FATAL', 'Handler maps non-existent function <%s> to command <%s>' % (function, command), exit_code=1)
        handler.mappings.append((command, handler.functions[function]))

    for special in handlers_xml.findall('special'):
        special_type = required_attribute(special, 'type')
        rewrite = required_attribute(special, 'rewrite')
        if not special_type in handler.specials.keys():
            log('FATAL', 'Special handler tag references unsupported type <%s>' % special_type, exit_code=1)
        handler.specials[special_type] = rewrite.encode('ascii')


def process_stance(stance_xml):
    for instance in stance_xml.findall('stance'):
        new_stance = feats.Stance(instance)
        log('STANCE', 'Added new stance [%s]' % new_stance.name)
        feats.stances[new_stance.name]=new_stance
        if new_stance.default:
            feats.default_stances.append(new_stance)

