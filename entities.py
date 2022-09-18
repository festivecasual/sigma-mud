import random
import uuid

import libsigma
import feats
from durations import Wait,Bonus
from world import World
from common import *


class Entity(object):
    def __init__(self):
        self.name = ''
        self.contents = []
        self.capacity = 0
        self.location = ''
        self.money = 0

        self._desc = ''
        self._keywords = []
        self._short = ''

        self.id = uuid.uuid4()

    @property
    def desc(self):
        return self._desc

    @property
    def short(self):
        return self._short

    @property
    def keywords(self):
        return self._keywords


class Item(Entity):
    def __init__(self, node):
        super(Item, self).__init__()

        self.weapon=None
        self.ammo=None
        self.wearable=None

        self.name = strip_whitespace(required_child(node, 'name').text)
        self._desc = wordwrap(strip_whitespace(required_child(node, 'desc').text))
        self._short = wordwrap(strip_whitespace(required_child(node, 'short').text))
        self._short_multiple = self._short
        self.flags = []

        self._quantity=INFINITE
        self.stackable=False
        self.max_quantity=1

        keywords = node.find('keywords')
        if keywords != None:
            self._keywords.extend(strip_whitespace(keywords.text).lower().split())

        s = node.find('stackable')
        if s != None:
            self.stackable=True
            self.max_quantity=required_attribute(s, 'max', int)

        for flag in node.findall('flag'):
            self.flags.append(strip_whitespace(flag.text))

        sm = node.find('short_multiple')
        if sm != None:
            self._short_multiple=strip_whitespace(sm.text)

        weapon = node.find('weapon')
        if weapon != None:
            self.weapon = Weapon(weapon)

        wearable = node.find('wearable')
        if wearable != None:
            self.wearable = Wearable(wearable,self.id)

        ammo = node.find('ammo')
        if ammo != None:
            self.ammo = Ammo(ammo)
        
    @property
    def short(self):
        if not self.stackable or self.quantity==1:
            return self._short
        else:
            return self._short_multiple

    def set_quantity(self, val):
        self._quantity = max(0, int(val))
        if self._quantity > self.max_quantity:
            self._quantity = self.max_quantity

    quantity = property(lambda self: self._quantity, set_quantity)


class Weapon(object):
    def __init__(self, node):
        self.strength_multiplier = 0.0
        self.accuracy_multiplier = 1.0
        self.two_handed = False
        self.damage = {}

        self.weapon_type = required_attribute(node, 'type')
        if self.weapon_type not in weapon_types:
            log("FATAL", "Unknown weapon type: '%s'" % self.weapon_type, exit_code=1)

        ac = node.find('accuracy')
        if ac != None:
            self.accuracy_multiplier = required_attribute(ac, 'multiplier', cast=float)

        for d in node.findall('damage'):
            damage_type = required_attribute(d, 'type')
            if damage_type not in damage_types:
                log("FATAL", "Unknown damage type: '%s'" % damage_type, exit_code=1)
            damage_multiplier = required_attribute(d, 'multiplier', cast=float)
            self.damage[damage_type] = damage_multiplier


class Wearable(object):
    def __init__(self, node,id):
        self.protection = {}
        self.absorption = {}
        self.bonuses=[]
        
        self.worn_position = required_attribute(node, 'position')
        if self.worn_position not in worn_positions:
            log("FATAL", "Unknown worn position: '%s'" % self.worn_position, exit_code=1)

        for p in node.findall('protection'):
            protection_type = required_attribute(p, 'type')
            if protection_type not in damage_types:
                log("FATAL", "Unknown protection (damage) type: '%s'" % protection_type, exit_code=1)
            protection_amount = required_attribute(p, 'amount', cast=float)
            self.protection[protection_type] = protection_amount

        for a in node.findall('absorption'):
            absorption_type = required_attribute(a, 'type')
            if absorption_type not in damage_types:
                log("FATAL", "Unknown absorption (damage) type: '%s'" % absorption_type, exit_code=1)
            absorption_value = required_attribute(a, 'amount', int)
            self.absorption[absorption_type] = absorption_value

        for b in node.findall('bonus'):
            stat = required_attribute(b,'stat')
            if stat not in stats:
                log("FATAL", "Unknown stat '%s'" % stat, exit_code=1)
            value= required_attribute(b,'value', cast=float)
            condition=required_attribute(b,'condition')
            if condition not in conditions:
                log("FATAL", "Unknown condition '%s'" % condition, exit_code=1)
            contexts=[]
            operator=required_attribute(b,'operator')
            if operator not in bonus_operators:
                log("FATAL", "Unknown operator '%s'" % condition, exit_code=1)
            duration=INFINITE
            d = b.get('duration',None)
            if d!=None:
                try:
                    duration=int(d)
                except ValueError:
                    log("FATAL", "Expecting integer for duration value")
            
            for c in b.findall('context'):
                contexts.append(required_attribute(c,'type'))
            self.bonuses.append(Bonus(stat,value,operator,contexts, id,'worn',duration,condition))
          
class Ammo(object):
    def __init__(self, node):
        self.damage = {}

        self.ammo_type = required_attribute(node, 'type')
        if self.ammo_type not in ammo_types:
            log("FATAL", "Unknown ammo type: '%s'" % self.ammo_type, exit_code=1)

        for d in node.findall('damage'):
            damage_type = required_attribute(d, 'type')
            if damage_type not in damage_types:
                log("FATAL", "Unknown damage type: '%s'" % damage_type, exit_code=1)
            damage_multiplier = required_attribute(d, 'multiplier', cast=float)
            self.damage[damage_type] = damage_multiplier


class Character(Entity):
    def __init__(self):
        super(Character, self).__init__()
        self.reset()

    def reset(self):
        self.gender=GENDER_NEUTRAL
        self.race=RACE_NEUTRAL

        self.level=0
        self._balance=0
        self._HP=0
        self._XP=0
        self.hidden=False
        self._MP=0
        self.spell_chanting=None
        self.spell_chanting_complete=False

        self.offers=[]
        self.stances=[]
        self.spells=[]
        self.waits=[]
        self.cooldowns=[]
        self.flags=[]
        self._bonuses=[]
        
        self.equipped_weapon=[]
        self.equipped_shield=None
        self._skin_protection={}
        self._skin_absorption={}
        self.worn_items=[]

        self.combats=[]
        self.engaged=None
        self.default_stance={}

        self.stats=dict.fromkeys(stats, DEFAULT_STAT)
        self.points_to_allocate=0

        [self.add_stance(s) for s in feats.default_stances]
        self.active_stance=self.stances[0]

        self.state=STATE_NULL

    def send_prompt(self): pass

    def send(self, s = ""): pass

    def send_line(self, s = "", breaks = 1): pass

    def send_combat_status(self): pass

    def handle_death(self):
        pass

    def check_level(self):
        pass

    @property
    def preferred_weapon_range(self):
        return max([preferred_range[w.weapon.weapon_type] for w in self.equipped_weapon if w.weapon]) if self.equipped_weapon else MELEE_RANGE

    @property
    def max_HP(self):
        return 4*self.stats["strength"] + 2*self.stats["discipline"]
    
    @property
    def max_MP(self):
        return 4*self.stats["intelligence"] + 2*self.stats["discipline"]

    @property
    def epitaph(self):
        return '%s has died.' % self.name

    def set_HP(self, val):
        self._HP = min(max(0, val), self.max_HP)
        if self._HP == 0:
            self.handle_death()


    HP = property(lambda self: self._HP, set_HP)

    def set_XP(self, val):
        self._XP = val
        self.check_level()

    XP = property(lambda self: self._XP, set_XP)

    def set_MP(self,val):
        self._MP = min(max(0,val),self.max_MP)
    
    MP = property(lambda self:self._MP,set_MP)

    def change_balance(self, val):
        self._balance = min(max(val, MIN_BALANCE), MAX_BALANCE)
        return

    balance = property(lambda self: self._balance, change_balance)

    def get_effective_all_context(self):
        ret_val={}
        for stat in stats:
            ret_val[stat]=self.effective_stat(stat,ALL_CONTEXT)
        return ret_val
   
    @property
    def bonuses(self):   
        for b in self._bonuses[:]:
            if b.duration_expired():
                self._bonuses.remove(b)
            else:
                yield b
        
    def effective_stat(self,stat,contexts):
        if stat not in stats:
            log("STAT CHECK", "Bad stat requested from %s" % self.id)
            return stat
        value_of_stat=self.stats[stat]
        for b in self.bonuses:
            for bc in b.context:
                if (bc in contexts or bc==ALL_CONTEXT) and b.stat==stat:
                    value_of_stat=b.apply_bonus(value_of_stat)
                    break   
        return int(value_of_stat)
        
    def can_equip(self, w_type):
        return w_type in [s.weapon_type for s in self.stances]

    def add_stance(self, stance):
        if stance.name in [s.name for s in self.stances]:
            return False

        if stance.weapon_type not in self.default_stance:
            self.default_stance[stance.weapon_type] = stance

        self.stances.append(stance)
        return True

    def get_protection_multiplier(self, damage_type):
        protection_value = sum([w.wearable.protection[damage_type] for w in self.worn_items if damage_type in w.wearable.protection])
        if protection_value == 0 and damage_type in self._skin_protection:
            return 1.0 - self._skin_protection[damage_type]
        else:
            return 1.0 - protection_value

    def get_absorption(self, damage_type):
        absorption_value = sum([w.wearable.absorption[damage_type] for w in self.worn_items if damage_type in w.wearable.absorption])
        if absorption_value == 0 and damage_type in self._skin_absorption:
            return self._skin_absorption[damage_type]
        else:
            return absorption_value

    def has_waits(self, prior=HIGHEST_PRIORITY):
        return False

    def has_cooldowns(self,categories=None):
        return False

    def reference_bonuses(self,bonuses,condition):
        for b in bonuses:
            if b.condition==condition:
                if b.operator=="*":
                    self._bonuses.insert(0,b)
                elif b.operator=="+":
                    self._bonuses.append(b)
                b.start_bonus_timer()
    
    def dereference_bonuses(self,id):
        for b in self._bonuses[:]:
            if b.source==id:
                self._bonuses.remove(b)
    
    def has_spell(self,spell_abbreviation):
        for spell in self.spells:
            if spell_abbreviation in spell.abbreviation:
                return spell
        return False

    def can_cast_spell(self,spell,target):
    #A check here would be good to override this check. But for now, all we'll do is ask the spell
    #if the requirements are met
        return spell.requirements_met(self,target)

    def finish_chanting(self):
        self.spell_chanting_complete=True
        self.send_line("You are finished preparing " + self.spell_chanting.name + ".")

class Denizen(Character):
    def __init__(self, node):
        super(Denizen, self).__init__()

        self.state = STATE_PLAYING

        self.name = strip_whitespace(required_child(node, 'name').text)
        self._desc = wordwrap(strip_whitespace(required_child(node, 'desc').text))
        self._short = wordwrap(strip_whitespace(required_child(node, 'short').text))
        self._epitaph = None

        epitaph = node.find('epitaph')
        if epitaph != None:
            self._epitaph = wordwrap(strip_whitespace(epitaph.text))

        keywords = node.find('keywords')
        if keywords != None:
            self._keywords.extend(strip_whitespace(keywords.text).lower().split())

        for flag in node.findall('flag'):
            self.flags.append(strip_whitespace(flag.text))

        stat_info = node.find('stats')
        if stat_info != None:
            self.level = required_attribute(stat_info, 'level', int)

            for stat in stats:
                #TODO: Obviously needs sophistication
                self.stats[stat] = self.level * 2

            for forced_stat in stat_info.findall('stat'):
                try:
                    self.stats[required_attribute(forced_stat, 'name')] = required_attribute(forced_stat, 'value', int)
                except KeyError:
                    log("FATAL", "<stat /> name attribute references an invalid statistic", exit_code=1)

        self.HP = self.max_HP

        for p in node.findall('protection'):
            protection_type = required_attribute(p, 'type')
            protection_value = required_attribute(p, 'amount', float)
            try:
                self._skin_protection[protection_type] = protection_value
            except KeyError:
                log("FATAL", "<protection /> element references an unknown protection (damage) type", exit_code=1)

        for a in node.findall('absorption'):
            absorption_type = required_attribute(a, 'type')
            absorption_value = required_attribute(a, 'amount', int)
            try:
                self._skin_absorption[absorption_type] = absorption_value
            except KeyError:
                log("FATAL", "<absorption /> element references an unknown absorption (damage) type", exit_code=1)

        for s in node.findall('stance'):
            name = required_attribute(s, 'name')
            active = (strip_whitespace(s.get('active', 'false')) == 'true')

            try:
                self.add_stance(feats.stances[name])
            except KeyError:
                log("FATAL", "Denizen <stance /> references unknown stance '%s'" % name, exit_code=1)

            if active:
                self.active_stance = feats.stances[name]

        m = node.find('money')
        if m != None:
            min_money=required_attribute(m, 'min', int)
            max_money=required_attribute(m, 'max', int)
            self.money=random.randint(min_money, max_money)

    @property
    def epitaph(self):
        if self._epitaph:
            return self._epitaph
        else:
            return super(Denizen, self).epitaph

    def handle_death(self):
        w = World()
        del w.denizens[self.id]
        libsigma.report(libsigma.ROOM, self.epitaph, self)
        #corpse=pickle.loads(items_source[CORPSE_REFERENCE])
        #self.location.contents.append(corpse)
        #libsigma.transfer_money(self.money,self,corpse)
        self.location.characters.remove(self)

class Player(Character):
    def __init__(self, s=None):
        super(Player, self).__init__()

        self.reset()

        self.socket = s
        if self.socket is not None:
            self.send_prompt()

    def reset(self):
        super(Player, self).reset()

        self.password = None
        self.state = STATE_INIT

    @property
    def desc(self):
        return "%s is here." % self.name

    @property
    def short(self):
        return "%s is here." % self.name

    @property
    def keywords(self):
        return [self.name.lower()]

    @property
    def epitaph(self):
        return '%s stumbles, falls to the ground, and breathes one last breath.' % self.name

    def send_prompt(self):
        self.send(prompts[self.state])

        if (self.state == STATE_INIT):
            self.state = STATE_NAME
            self.send_prompt()

    def send(self, s=""):
        b = bytes(s, encoding='ascii')
        self.socket.push(b)

    def send_line(self, s="", breaks=1):
        self.send(s)
        self.send("\r\n" * breaks)

    def send_combat_status(self):
        self.send_line("[HP: %d/%d | Balance: %s]" % (self.HP, self.max_HP, balance_name[self.balance]))

    def handle_death(self):
        pass

    def has_cooldowns(self,categories=[]):
        for c in self.cooldowns:
            if (not c.duration_expired() and set(c.categories).intersection(categories) !=[]):
                return c.remaining_time()
        return False

    def has_waits(self,prior=HIGHEST_PRIORITY):
        for w in self.waits:
            if (not w.duration_expired()) and w.priority <= prior:
                return w.remaining_time()
        return False

    def add_wait(self, p, d):
        self.waits.append(Wait(p,d))
        self.send_line("[This action adds a %d second wait]" % d)
        return
