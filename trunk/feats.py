from common import *
import libsigma

stances={}
default_stances=[]

class stance(object):
    def __init__(self, node):
        
        self.name = strip_whitespace(required_child(node, 'name').text)
        self.desc = wordwrap(strip_whitespace(required_child(node, 'desc').text))
        self.weapon_type=libsigma.txt2val(wordwrap(strip_whitespace(required_child(node, 'weapontype').text)), weapon_match_txt,weapon_match_val)
        
        self.default=False
        
        
        default_overwrite=strip_whitespace(node.find('default').text)
        if default_overwrite.lower() =="true":
            self.default=True
       
         
        #balance modifiers
        self.balance={}
        
        #If a successful hit occurs in this stance, the rate 
        #at which a balance increase occurs and the magnitude 
        #in which balance is increased.
        self.balance["HitIncreasePercent"]=50
        self.balance["HitIncreaseAmount"]=1
        
        #...on a miss
        self.balance["MissIncreasePercent"]=50
        self.balance["MissIncreaseAmount"]=-1
        
        #...on receiving a hit
        self.balance["HitReceivedIncreasePercent"]=25
        self.balance["HitReceivedIncreaseAmount"]=-1
        
        #...on dodging/blocking(?) an attack
        self.balance["DodgeIncreasePercent"]=25
        self.balance["DodgeIncreaseAmount"]=1
        
        #...on a critical strike, the modification of a successful chance
        #and amount of balance granted
        self.balance["CriticalChanceModifier"]=1.5
        self.balance["CriticalAmountModifier"]=2
        
        
        for child in node.find('balance'):
            if self.balance.has_key(child.tag):
                self.balance[child.tag]=float(child.text)
        
        # damage modifiers
        self.damage={}
        self.critical_percent=5
        
        if self.weapon_type==BARE_HAND:
            self.damage[IMPACT]=1.0
            
        for child in node.findall('damages'):
            for d in child.findall('damage'):
                damage_name = required_attribute(d, 'type')
                damage_multiplier = required_attribute(d, 'multiplier')
                self.damage[int(libsigma.txt2val(damage_name,damage_match_txt,damage_match_val))]=float(damage_multiplier)
                