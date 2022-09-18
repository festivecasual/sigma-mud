import random

import libsigma
from world import World
from common import *


class Combat(object):
    def __init__(self, combatant1, combatant2):
        # combatant1 is assumed the aggressor. He is assumed to be
        # engaged initially in this combat, as s/he instigated it
        self.combatants=[]

        self.combatants.append(combatant1)
        self.combatants.append(combatant2)

        self.actions=[None,None]
        self.override_ranges=[None,None]
        self.discard={}
        self.retreat_direction=[None,None]

        self.combatant1 = combatant1
        self.combatant2 = combatant2

        self.combatant1_action = None
        self.combatant2_action = None

        self.churn=0

        self.combatant1_override_range=None
        self.combatant2_override_range=None

        self.combatant1_discard=[]
        self.combatant2_discard=[]

        self.combatant1_retreat_direction=None
        self.combatant2_retreat_direction=None

        self.strike_queue = []

        self.combat_state = COMBAT_STATE_INITIALIZING
        self.range = NOT_IN_COMBAT

    def get_opponent(self,combatant):
        for c in self.combatants:
            if c != combatant:
                return c
        return False

    def get_combatant1(self):
        return self.combatant[0]

    def get_combatant2(self):
        return self.combatant[1]

    def send_combat_statuses(self):
        for c in self.combatants:
            c.send_combat_status()

    def engage_combatants(self):
        self.combatants[0].engaged=self

        libsigma.report(libsigma.SELF|libsigma.ROOM, "$actor $verb advancing toward $direct!",self.combatants[0],("are","is"),self.combatants[1])
        self.send_combat_statuses()
        if not self.combatants[1].engaged:
            libsigma.report(libsigma.SELF|libsigma.ROOM, "$actor $verb for the attack!",self.combatants[0],("ready","readies"))
            self.send_combat_statuses()
            self.combatants[1].engaged = self

    def evaluate_range(self):
            #if self.combatants[0].preferred_weapon_range==self.combatants[1].preferred_weapon_range:
            if self.get_preferred_range(self.combatants[0]) == self.get_preferred_range(self.combatants[1]):
                return self.get_preferred_range(self.combatants[0])
            else:
                #set up chance to make it to desired range according to combatant1
                #TODO: Will have to be rewritten when bonsuses come on...
                #this is a real simple implementation anyway
                agil_diff=self.combatants[0].stats["agility"] - self.combatants[1].stats["agility"]
                range_request_diff= self.get_preferred_range(self.combatants[0]) -  self.get_preferred_range(self.combatants[1])
                percent_success=min(max(4*agil_diff+10*range_request_diff + 50, 5), 95)
                roll_for_range=libsigma.d100()
                # libsigma.report(libsigma.SELF|libsigma.ROOM, "Roll was: " + str(roll_for_range) + " and threshold for success for $actor was: " + str(percent_success),c.combatant1 )
                if roll_for_range  <= percent_success:
                    return  self.get_preferred_range(self.combatants[0])
                else:
                    return  self.get_preferred_range(self.combatants[1])

    def release(self,victor):
        w = World()
        w.combats.remove(self)
        self.combatant1.combats.remove(self)
        self.combatant2.combats.remove(self)

        for combatant in [self.combatant1, self.combatant2]:
            if combatant.engaged==self:
                if combatant.combats:
                    combatant.engaged=self.combatant1.combats[0]
                    combatant.engaged.in_range_set_action(combatant)
                else:
                    combatant.engaged=None

        victor_discard = self.get_discard(victor)
        loser = self.get_opponent(victor)
        for d in victor_discard:
            if d.stackable:
                d_a=0
                for a in range(d.quantity):
                    roll=libsigma.d100()
                    if roll<=75:
                        d_a+=1
                libsigma.transfer_item(d,victor_discard,victor.contents,d_a)
                victor.send_line("You recover " + str(d_a) + " of " + d.name + "!")
            else:
                roll=libsigma.d100()
                if roll<=80:
                    libsigma.transfer_item(d,self.victor_discard,victor.contents)
                    victor.send_line("You recover " + d.name + "!")

    def queue_strikes(self):
        #TODO: Section needs work. Defaults to attack, need to do more checks

        if self.combatant1_action == COMBAT_ACTION_ATTACKING and self.combatant2_action != COMBAT_ACTION_ATTACKING:
            self.strike_queue.append((self.combatant1,self.combatant2))
            self.strike_queue.append((self.combatant2,self.combatant1))
            return
        elif self.combatant2_action == COMBAT_ACTION_ATTACKING and self.combatant1_action != COMBAT_ACTION_ATTACKING:
            self.strike_queue.append((self.combatant2,self.combatant1))
            self.strike_queue.append((self.combatant1,self.combatant2))
            return
        else:
            agil_diff=self.combatant1.stats["agility"] - self.combatant2.stats["agility"]
            percent_success=min(max(agil_diff*5 + 50, 20), 80)
            roll_for_first_strike=libsigma.d100()
            if roll_for_first_strike <= percent_success:
                self.strike_queue.append((self.combatant1, self.combatant2))
                self.strike_queue.append((self.combatant2, self.combatant1))
            else:
                self.strike_queue.append((self.combatant2, self.combatant1))
                self.strike_queue.append((self.combatant1, self.combatant2))
            # end section

    def in_range_set_action(self,one_combatant=None):
        weapon_type=[]
        for c in self.combatants:
            weapon_type.append('bare handed' if not c.equipped_weapon else c.equipped_weapon[0].weapon.weapon_type)

        do_change=[True,True]
        old_actions=[self.get_action(self.combatants[0]),self.get_action(self.combatants[1])]
        if one_combatant==self.combatants[0]:
            do_change[0]=True
            do_change[1]=False
        elif one_combatant==self.combatants[1]:
            do_change[0]=False
            do_change[1]=True

        for x in range(len(self.combatants)):
            if do_change[x]:
                if self.range in weapon_range[weapon_type[x]] and self.combatants[x].engaged==self:
                    self.set_action(self.combatants[x],COMBAT_ACTION_ATTACKING)
                    if old_actions[x]!=self.actions[x]:
                        self.combatants[x].send_line("You are set to attack!")
                        #self.combatants[x].send_combat_status()
                elif (self.actions[x] == COMBAT_ACTION_ADVANCING or self.actions[x]==COMBAT_ACTION_WITHDRAWING) and self.get_preferred_range(self.combatants[x])==self.range:
                    self.combatants[x].send_line("You can't attack from this range!")
                    self.set_action(self.combatants[x],COMBAT_ACTION_IDLE)
                elif self.actions[x] not in (COMBAT_ACTION_WITHDRAWING,COMBAT_ACTION_ADVANCING):
                    self.set_action(self.combatants[x],COMBAT_ACTION_IDLE)
                    

        return

    def get_discard(self,playr):
        return self.combatant1_discard if self.combatant1==playr else self.combatant2_discard

    def get_preferred_range(self,playr):
        for x in range(len(self.combatants)):
            if self.combatants[x]==playr:
                if self.override_ranges[x]:
                    return self.override_ranges[x]
                else:
                    return self.combatants[x].preferred_weapon_range

        log("COMBAT", "Call to get_action references an invalid player")
        return -1

    def get_action(self,playr):
        for x in range(len(self.combatants)):
            if self.combatants[x]==playr:
                return self.actions[x]

        log("COMBAT", "Call to get_action references an invalid player")
        return -1

    def set_action(self,playr,action):
        for x in range(len(self.combatants)):
            if self.combatants[x]==playr:
                self.actions[x]=action
                return

    def set_override_range(self,playr,value):
        for x in range(len(self.combatants)):
            if self.combatants[x]==playr:
                self.override_ranges[x]=value
                return

    def set_retreat(self,coward,direction):
        if coward==self.combatant1:
            self.combatant1_action=COMBAT_ACTION_RETREATING
            self.combatant1_retreat_direction=direction
        else:
            self.combatant2_action=COMBAT_ACTION_RETREATING
            self.combatant2_retreat_direction=direction

    def is_retreat_successful(self,coward):
        adversary_agility=self.combatant1.stats["agility"] if coward!=self.combatant1 else self.combatant2.stats["agility"]
        return libsigma.roll_for_success(coward.stats["agility"],adversary_agility,30,100,2,65)

    def retreat(self,coward):
        w = World()
        for co in coward.combats:
            w.combats.remove(co)
            co.combatant1.combats.remove(co)
            co.combatant2.combats.remove(co)
            if co.combatant1.engaged==co:
                if co.combatant1.combats and co.combatant1 != coward:
                    co.combatant1.engaged=co.combatant1.combats[0]
                    co.combatant1.engaged.in_range_set_action(co.combatant1)
                else:
                    co.combatant1.engaged=None

            if co.combatant2.engaged==co:
                if co.combatant2.combats and co.combatant2 != coward:
                    co.combatant2.engaged=co.combatant2.combats[0]
                    co.combatant2.engaged.in_range_set_action(co.combatant2)
                else:
                    co.combatant2.engaged=None
        choices=[]
        choices.extend(libsigma.open_exits(coward.location))
        selection = random.choice(choices)
        libsigma.report(libsigma.SELF|libsigma.ROOM, "$actor $verb to turn tail and run away!", coward,("manage", "manages"))
        libsigma.run_command(coward, "go " + libsigma.dir2txt(selection))


class Damage(object):
    def __init__(self):
        return
