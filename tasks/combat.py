import world
import libsigma
from common import *


# Proper name of task
name = 'Combat Manager'
interval = 2


def task_init():
    pass


def task_execute():  # moves all combats through states through its lifecycle
    for c in world.combats:
        if c.combat_state==COMBAT_STATE_INITIALIZING:  # Initializing is defined as a combat that has just begun.
            c.combatant1.engaged = c
            c.combatant1.send_combat_status()
            c.combatant2.send_combat_status()
            c.combat_state = COMBAT_STATE_ENGAGING

            libsigma.report(libsigma.SELF|libsigma.ROOM, "$actor $verb advancing toward $direct!",c.combatant1,("are","is"),c.combatant2)
            if not c.combatant2.engaged:
                libsigma.report(libsigma.SELF|libsigma.ROOM, "$actor $verb $direct for the attack!",c.combatant2,("ready","readies"),c.combatant2)
                c.combatant2.engaged = c

        elif c.combat_state == COMBAT_STATE_ENGAGING:
            if c.combatant1.preferred_weapon_range==c.combatant2.preferred_weapon_range:
                c.range=c.combatant1.preferred_weapon_range
            else:
                #set up chance to make it to desired range according to combatant1
                #will have to be rewritten when bonsuses come on...
                #this is a real simple implementation anyway
                agil_diff=c.combatant1.stats["agility"] - c.combatant2.stats["agility"]
                range_request_diff=c.combatant1.preferred_weapon_range - c.combatant2.preferred_weapon_range
                percent_success=min(max(4*agil_diff+10*range_request_diff + 50, 5), 95)
                roll_for_range=libsigma.d100()
                # libsigma.report(libsigma.SELF|libsigma.ROOM, "Roll was: " + str(roll_for_range) + " and threshold for success for $actor was: " + str(percent_success),c.combatant1 )
                if roll_for_range  <= percent_success:
                    c.range=c.combatant1.preferred_weapon_range
                else:
                    c.range=c.combatant2.preferred_weapon_range

            libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor and $direct clash into combat at " + libsigma.val2txt(c.range,range_match_val,range_match_txt) +" range!",c.combatant1,None,c.combatant2)
            c.combatant1.send_combat_status()
            c.combatant2.send_combat_status()
            

            c.in_range_set_action()
            
            c.queue_strikes()

            c.combat_state=COMBAT_STATE_FIGHTING
            break

        elif c.combat_state == COMBAT_STATE_FIGHTING:
            # Strange case when strike queue is empty at this point
            if not c.strike_queue:
                c.combat_state = COMBAT_STATE_INTERMISSION
                break
            
            striker, defender, striker_state,striker_preferred_range = c.strike_queue[0]
            ## roll for hit -- Agility
            if striker_state==COMBAT_ACTION_ATTACKING:
                striker_effective_agil=int(striker.stats["agility"]*balance_multiplier[striker.balance])
                defender_effective_agil=int(defender.stats["agility"]*balance_multiplier[defender.balance]) 
                agil_diff=striker_effective_agil - defender_effective_agil
    
                percent_success=min(max(agil_diff * 3 + 75, 40), 98)
                roll_for_hit=libsigma.d100()
                if roll_for_hit <= percent_success:
                    #hit
                    damage = calculate_damage(striker, defender,c.range)
                    libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor successfully $verb $direct for " + str(damage) +" damage!", striker,("hit","hits"), defender)
                  
                    if (defender.HP - damage) <= 0:
                        libsigma.report(libsigma.SELF | libsigma.ROOM, "$actor $verb victorious over $direct!",striker,("are","is"),defender)
                        c.release()
                    defender.HP -= damage
                    striker_roll_for_balance=libsigma.d100()
                    defender_roll_for_balance=libsigma.d100()
                    if striker_roll_for_balance<striker.active_stance.balance["HitIncreasePercent"]:
                        striker.balance += striker.active_stance.balance["HitIncreaseAmount"]
                    if defender_roll_for_balance<defender.active_stance.balance["HitReceivedIncreasePercent"]:
                        defender.balance += defender.active_stance.balance["HitReceivedIncreaseAmount"]
    
                            
                else:
                    #miss
                    libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor $verb in an attempt to attack $direct!" ,striker,("miss","misses"),defender)
                    striker_roll_for_balance=libsigma.d100()
                    defender_roll_for_balance=libsigma.d100()
                    if striker_roll_for_balance<striker.active_stance.balance["MissIncreasePercent"]:
                        striker.balance += striker.active_stance.balance["MissIncreaseAmount"]
                    if defender_roll_for_balance<defender.active_stance.balance["DodgeIncreasePercent"]:
                        defender.balance += defender.active_stance.balance["DodgeIncreaseAmount"]
           
            elif striker_state==COMBAT_ACTION_IDLE:
                libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor $verb at $direct, unable to attack!", striker, ("glare", "glares"), defender)
                if type(striker)==world.denizen:
                    if striker.preferred_weapon_range < c.range:
                        libsigma.run_command(striker, "advance")
                    else:
                        libsigma.run_command(striker, "withdraw")
            elif striker_state==COMBAT_ACTION_ADVANCING:
                agil_diff=striker.stats["agility"] - defender.stats["agility"]
                range_request_diff=striker_preferred_range - c.range
                percent_success=min(max(4*agil_diff+10*range_request_diff + 50 + (10*c.churn), 5), 95)
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
                
            elif striker_state==COMBAT_ACTION_WITHDRAWING:
                agil_diff=striker.stats["agility"] - defender.stats["agility"]
                range_request_diff= c.range-striker_preferred_range
                percent_success=min(max(4*agil_diff+10*range_request_diff + 50 + (10*c.churn), 5), 95)
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


def calculate_damage(attacker, defender,combat_range):
    damage = 0
    attacker_damage={}
    if  attacker.active_stance.weapon_type==BARE_HAND:

        for damage_type in damage_match_val:
            if attacker.active_stance.damage.has_key(damage_type):
                attacker_damage[damage_type]=attacker.stats["strength"]
                attacker_damage[damage_type]*=weapon_damage_multiplier[BARE_HAND]
                attacker_damage[damage_type]*=weapon_range[BARE_HAND][combat_range]
                attacker_damage[damage_type]*=attacker.active_stance.damage[damage_type]
                
                #defense calculations
                attacker_damage[damage_type]*=defender.get_protection_multiplier(damage_type)
                attacker_damage[damage_type]=max(attacker_damage[damage_type]-defender.get_absorption(damage_type),0)
                damage+=attacker_damage[damage_type]
            else:
                attacker_damage[damage_type]=0     
    else:  
        for w in attacker.equipped_weapon:
            for damage_type in damage_match_val:
                if w.damage.has_key(damage_type):
                    attacker_damage[damage_type]=attacker.stats["strength"]
                    attacker_damage[damage_type]*=weapon_damage_multiplier[w.weapon_type]
                    attacker_damage[damage_type]*=weapon_range[w.weapon_type][combat_range]
                    attacker_damage[damage_type]*=w.damage[damage_type]
                
                    #defense calculations
                    attacker_damage[damage_type]*=defender.get_protection_multiplier(damage_type)
                    attacker_damage[damage_type]=max(attacker_damage[damage_type]-defender.get_absorption(damage_type),0)
                    #log("TEST", str(defender.get_protection_multiplier(damage_type)) + " " + libsigma.val2txt(damage_type,damage_match_val,damage_match_txt))
                    #log("TEST", str(defender.get_absorption(damage_type)) + " " + libsigma.val2txt(damage_type,damage_match_val,damage_match_txt))
                    damage+=attacker_damage[damage_type]
                else:
                    attacker_damage[damage_type]=0   
    
    
                
                
    return int(round(damage))