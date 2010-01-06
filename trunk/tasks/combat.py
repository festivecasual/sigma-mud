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

            c.queue_strikes()

            c.combat_state=COMBAT_STATE_FIGHTING
            break

        elif c.combat_state == COMBAT_STATE_FIGHTING:
            # Strange case when strike queue is empty at this point
            if not c.strike_queue:
                c.combat_state = COMBAT_STATE_INTERMISSION
                break

            striker, defender = c.strike_queue[0]
            ## roll for hit -- Agility
            agil_diff=striker.stats["agility"] - defender.stats["agility"]
            percent_success=min(max(agil_diff * 3 + 75, 40), 98)
            roll_for_hit=libsigma.d100()
            if roll_for_hit <= percent_success:
                #hit
                damage = calculate_damage(striker, defender)
                libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor successfully $verb $direct for " + str(damage) +" damage!", striker,("hit","hits"), defender)
                if (defender.HP - damage) <= 0:
                    libsigma.report(libsigma.SELF | libsigma.ROOM, "$actor $verb victorious over $direct!",striker,("are","is"),defender)
                    c.release()
                defender.HP -= damage
            else:
                #miss
                libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor $verb in an attempt to attack $direct!" ,striker,("miss","misses"),defender)

            c.strike_queue = c.strike_queue[1:]
            if not c.strike_queue:
                c.combat_state = COMBAT_STATE_INTERMISSION

        elif c.combat_state == COMBAT_STATE_INTERMISSION:
            c.queue_strikes()
            c.combat_state=COMBAT_STATE_FIGHTING


def task_deinit():
    pass


def calculate_damage(attacker, defender):
    return attacker.stats["strength"]
