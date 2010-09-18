from common import *
import libsigma


stances={}
default_stances=[]


class Stance(object):
    def __init__(self, node):
        self.name = strip_whitespace(required_child(node, 'name').text)
        self.desc = wordwrap(strip_whitespace(required_child(node, 'desc').text))

        self.weapon_type = strip_whitespace(required_child(node, 'weapontype').text)
        if self.weapon_type not in weapon_types:
            log("FATAL", "Stance '%s' has unknown weapon type: '%s'" % (self.name, self.weapon_type), exit_code=1)

        self.default = node.find('default') != None

        # Balance modifiers
        self.balance={}

        # If a successful hit occurs in this stance, the rate
        # at which a balance increase occurs and the magnitude
        # in which balance is increased.
        self.balance["HitIncreasePercent"]=50.0
        self.balance["HitIncreaseAmount"]=1.0

        # ...on a miss
        self.balance["MissIncreasePercent"]=50.0
        self.balance["MissIncreaseAmount"]=-1.0

        # ...on receiving a hit
        self.balance["HitReceivedIncreasePercent"]=25.0
        self.balance["HitReceivedIncreaseAmount"]=-1.0

        # ...on dodging/blocking(?) an attack
        self.balance["DodgeIncreasePercent"]=25.0
        self.balance["DodgeIncreaseAmount"]=1.0

        # ...on a critical strike, the modification of a successful chance
        # and amount of balance granted
        self.balance["CriticalChanceModifier"]=1.5
        self.balance["CriticalAmountModifier"]=2.0

        for child in node.find('balance'):
            try:
                self.balance[child.tag]=float(child.text)
            except KeyError:
                log("FATAL", "Unknown key in stance '%s' balance: %s" % (self.name, child.tag), exit_code=1)
            except ValueError:
                log("FATAL", "Balance value %s in '%s' not a number" % (child.tag, self.name), exit_code=1)

        # Damage modifiers
        self.damage={}
        self.critical_percent=5

        if self.weapon_type=='bare handed':
            self.damage['impact']=1.0

        if node.find('damages') != None:
            for child in node.find('damages'):
                for d in child.findall('damage'):
                    damage_type = required_attribute(d, 'type')
                    if damage_type not in damage_types:
                        log("FATAL", "Unknown damage type %s in stance '%s'" % (damage_type, self.name), exit_code=1)
                    damage_multiplier = required_attribute(d, 'multiplier', float)
                    self.damage[damage_type] = damage_multiplier
