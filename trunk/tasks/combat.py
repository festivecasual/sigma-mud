import libsigma
import entities
from world import World
from common import *


# Proper name of task
name = 'Combat Manager'
interval = 2


def task_init():
    pass


def task_execute():  # moves all combats through states through its lifecycle
    w = World()
    for c in w.combats[:]:

        if c.combatant1_action==COMBAT_ACTION_RETREATING:
            retreat=True
            for co in c.combatant1.combats:
                if not co.is_retreat_successful(c.combatant1):
                    c.combatant1.send_line("You try to retreat, but cannot get away from " + (co.combatant1.name if co.combatant1!=c.combatant1 else c.combatant2.name) + "!")
                    retreat=False
            if retreat:
                c.retreat(c.combatant1)
                continue
        if c.combatant2_action==COMBAT_ACTION_RETREATING:
            retreat=True
            for co in c.combatant2.combats:
                if not co.is_retreat_successful(c.combatant2):
                    c.combatant2.send_line("You try to retreat, but cannot get away from " + (co.combatant1.name if co.combatant1!=c.combatant1 else c.combatant2.name) + "!")
                    retreat=False
            if retreat:
                c.retreat(c.combatant2)
                continue

        if c.combat_state==COMBAT_STATE_INITIALIZING:  # Initializing is defined as a combat that has just begun.
            c.engage_combatants()
            c.combat_state = COMBAT_STATE_ENGAGING

        elif c.combat_state == COMBAT_STATE_ENGAGING:
            c.range=c.evaluate_range()
            libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor and $direct clash into combat at " + libsigma.val2txt(c.range,range_match_val,range_match_txt) +" range!",c.combatant1,None,c.combatant2)
            c.send_combat_statuses()
            c.in_range_set_action()
            c.queue_strikes()
            c.combat_state=COMBAT_STATE_FIGHTING
            break

        elif c.combat_state == COMBAT_STATE_FIGHTING:
            # Strange case when strike queue is empty at this point
            if not c.strike_queue:
                c.combat_state = COMBAT_STATE_INTERMISSION
                break

            striker, defender = c.strike_queue[0]

            striker_action=c.get_action(striker)

            striker_preferred_range=c.get_preferred_range(striker)

            ## roll for hit -- Agility
            if striker_action==COMBAT_ACTION_ATTACKING:
                ammo=None
                can_strike=False
                if not striker.active_stance.weapon_type in ammo_weapons:
                    can_strike=True
                else:
                    for w in striker.equipped_weapon:
                        if w.ammo:
                            if ammo_requirements[striker.active_stance.weapon_type] == w.ammo.ammo_type:
                                can_strike=True
                                ammo=w


                if can_strike:
                    striker_effective_agil=int(striker.stats["agility"]*balance_multiplier[striker.balance])
                    defender_effective_agil=int(defender.stats["agility"]*balance_multiplier[defender.balance])
                    agil_diff= striker_effective_agil - defender_effective_agil

                    percent_success=min(max(agil_diff * 3 + 75, 40), 98)
                    roll_for_hit=libsigma.d100()

                    if roll_for_hit <= percent_success:
                        #hit
                        damage = calculate_damage(striker, defender,c.range,ammo)
                        if(striker.active_stance.weapon_type in ammo_weapons):
                            libsigma.transfer_item(ammo,striker.equipped_weapon,c.get_discard(striker),1)
                        libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor successfully $verb $direct for " + str(damage) +" damage!", striker,("hit","hits"), defender)

                        if (defender.HP - damage) <= 0:
                            libsigma.report(libsigma.SELF | libsigma.ROOM, "$actor $verb victorious over $direct!",striker,("are","is"),defender)
                            c.release(striker)
                        defender.HP -= damage
                        striker_roll_for_balance=libsigma.d100()
                        defender_roll_for_balance=libsigma.d100()
                        if striker_roll_for_balance<striker.active_stance.balance["HitIncreasePercent"]:
                            striker.balance += striker.active_stance.balance["HitIncreaseAmount"]
                        if defender_roll_for_balance<defender.active_stance.balance["HitReceivedIncreasePercent"]:
                            defender.balance += defender.active_stance.balance["HitReceivedIncreaseAmount"]


                    else:
                        #miss
                        if(striker.active_stance.weapon_type in ammo_weapons):
                            libsigma.transfer_item(ammo,striker.equipped_weapon,striker.location.contents,1,True)
                        libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor $verb in an attempt to attack $direct!" ,striker,("miss","misses"),defender)
                        striker_roll_for_balance=libsigma.d100()
                        defender_roll_for_balance=libsigma.d100()
                        if striker_roll_for_balance<striker.active_stance.balance["MissIncreasePercent"]:
                            striker.balance += striker.active_stance.balance["MissIncreaseAmount"]
                        if defender_roll_for_balance<defender.active_stance.balance["DodgeIncreasePercent"]:
                            defender.balance += defender.active_stance.balance["DodgeIncreaseAmount"]
                else:
                        libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor $verb at $direct, unable to attack!", striker, ("glare", "glares"), defender)

            elif striker_action==COMBAT_ACTION_IDLE:
                libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor $verb at $direct, unable to attack!", striker, ("glare", "glares"), defender)
                if type(striker)==entities.Denizen:
                    if striker.preferred_weapon_range < c.range:
                        libsigma.run_command(striker, "advance")
                    else:
                        libsigma.run_command(striker, "withdraw")
            elif striker_action==COMBAT_ACTION_ADVANCING:
                agil_diff=striker.stats["agility"] - defender.stats["agility"]
                range_request_diff=striker_preferred_range - c.range
                percent_success=min(max(4*agil_diff+10*range_request_diff + 50 + (20*c.churn), 5), 95)
                roll_for_range=libsigma.d100()

                if roll_for_range  <= percent_success:
                    c.range=striker_preferred_range
                    c.churn=0
                    libsigma.report(libsigma.SELF| libsigma.ROOM, "$actor $verb into " + libsigma.val2txt(c.range, range_match_val, range_match_txt) + " range with $direct!",striker,("close", "closes"), defender)
                    c.in_range_set_action()
                    c.strike_queue=[]
                else:
                    c.churn+=1
                    libsigma.report(libsigma.SELF| libsigma.ROOM, "$actor $verb to close into a closer range with $direct, but cannot!",striker,("try", "tries"), defender)

            elif striker_action==COMBAT_ACTION_WITHDRAWING:
                agil_diff=striker.stats["agility"] - defender.stats["agility"]
                range_request_diff= c.range-striker_preferred_range
                percent_success=min(max(4*agil_diff+10*range_request_diff + 50 + (20*c.churn), 5), 95)
                roll_for_range=libsigma.d100()

                if roll_for_range  <= percent_success:
                    c.range=striker_preferred_range
                    c.churn=0
                    libsigma.report(libsigma.SELF| libsigma.ROOM, "$actor $verb to " + libsigma.val2txt(c.range, range_match_val, range_match_txt) + " range with $direct!",striker,("withdraw", "withdraws"), defender)
                    c.in_range_set_action()
                    c.strike_queue=[]
                else:
                    c.churn+=1
                    libsigma.report(libsigma.SELF| libsigma.ROOM, "$actor $verb to withdraw to a further range with $direct, but cannot!",striker,("try", "tries"), defender)

            striker.send_combat_status()
            defender.send_combat_status()

            if c.strike_queue:
                c.strike_queue = c.strike_queue[1:]
            if not c.strike_queue:
                c.combat_state = COMBAT_STATE_INTERMISSION

        elif c.combat_state == COMBAT_STATE_INTERMISSION:
            c.queue_strikes()
            c.combat_state=COMBAT_STATE_FIGHTING


def task_deinit():
    pass


def calculate_damage(attacker, defender, combat_range, ammo):
    damage = 0
    attacker_damage={}
    if  attacker.active_stance.weapon_type=='bare handed':
        for damage_type in damage_types:
            if attacker.active_stance.damage.has_key(damage_type):
                attacker_damage[damage_type]=attacker.stats["strength"]
                attacker_damage[damage_type]*=weapon_damage_multiplier['bare handed']
                attacker_damage[damage_type]*=weapon_range['bare handed'][combat_range]
                attacker_damage[damage_type]*=attacker.active_stance.damage[damage_type]

                #defense calculations
                attacker_damage[damage_type]*=defender.get_protection_multiplier(damage_type)
                attacker_damage[damage_type]=max(attacker_damage[damage_type]-defender.get_absorption(damage_type),0)
                damage+=attacker_damage[damage_type]
            else:
                attacker_damage[damage_type]=0
    else:
        for w in attacker.equipped_weapon:
            for damage_type in damage_types:
                if w.weapon.damage.has_key(damage_type) or ammo:
                    attacker_damage[damage_type]=attacker.stats["strength"]
                    attacker_damage[damage_type]*=weapon_damage_multiplier[w.weapon.weapon_type]
                    attacker_damage[damage_type]*=weapon_range[w.weapon.weapon_type][combat_range]

                    if not ammo:
                        attacker_damage[damage_type]*=w.weapon.damage[damage_type]
                    elif ammo.ammo.damage.has_key(damage_type):
                        attacker_damage[damage_type]*=ammo.ammo.damage[damage_type]
                    else:
                        attacker_damage[damage_type]=0

                    #defense calculations
                    attacker_damage[damage_type]*=defender.get_protection_multiplier(damage_type)
                    attacker_damage[damage_type]=max(attacker_damage[damage_type]-defender.get_absorption(damage_type),0)

                    damage+=attacker_damage[damage_type]
                else:
                    attacker_damage[damage_type]=0

    return int(round(damage))