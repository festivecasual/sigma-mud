import world,libsigma
from common import *
## Proper name of task
name = 'Combat Manager'
interval = 2

def task_init():
    pass

def task_execute(): ## moves all combats through states through its lifecycle
    for c in world.combats:
        if c.combat_state==COMBAT_STATE_INITIALIZING: ## Initializing is defined as a combat that has just begun.            
            for d in c.combatant2.combats:
                if d!=c and ((d.combatant1_engaged==True and d.combatant1==c.combatant2) or (d.combatant2_engaged==True and d.combatant2==c.combatant2)):
                     c.combat_state=COMBAT_STATE_ENGAGING
                     libsigma.report(libsigma.SELF|libsigma.ROOM, "$actor $verb advancing toward $direct!",c.combatant1,("are","is"),c.combatant2)
                     c.combatant1.send_combat_status()
                     c.combatant2.send_combat_status()
                     break          
            c.combat_state=COMBAT_STATE_ENGAGING
            c.combatant2_engaged=True
            libsigma.report(libsigma.SELF|libsigma.ROOM, "$actor $verb advancing toward an anticipating $direct!",c.combatant1,("are","is"),c.combatant2)
            c.combatant1.send_combat_status()
            c.combatant2.send_combat_status()
            
            
        elif c.combat_state == COMBAT_STATE_ENGAGING:
            if c.combatant1_preferred_weapon_range==c.combatant2_preferred_weapon_range:
                c.range=c.combatant1_preferred_weapon_range
               
            else:
                #set up chance to make it to desired range according to combatant1
                #will have to be rewritten when bonsuses come on...
                #this is a real simple implementation anyway
                agil_diff=c.combatant1.stats["agility"] - c.combatant2.stats["agility"]
                range_request_diff=c.combatant1_preferred_weapon_range - c.combatant2_preferred_weapon_range
                percent_success=4*agil_diff+10*range_request_diff + 50
                if percent_success > 95:
                    percent_success = 95
                elif percent_success < 5:
                    percent_success = 5 
                roll_for_range=libsigma.d100()
               # libsigma.report(libsigma.SELF|libsigma.ROOM, "Roll was: " + str(roll_for_range) + " and threshold for success for $actor was: " + str(percent_success),c.combatant1 )
                if roll_for_range  <= percent_success:
                    c.range=c.combatant1_preferred_weapon_range
                else:
                    c.range=c.combatant2_preferred_weapon_range             
            
            libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor and $direct clash into combat at " + libsigma.val2txt(c.range,range_match_val,range_match_txt) +" range!",c.combatant1,None,c.combatant2) 
            c.combatant1.send_combat_status()
            c.combatant2.send_combat_status()
            # section needs work. Defaults to attack, need to do more checks
            c.combatant1_action=COMBAT_ACTION_ATTACKING
            c.combatant2_action=COMBAT_ACTION_ATTACKING
            agil_diff=c.combatant1.stats["agility"] - c.combatant2.stats["agility"]
            percent_success=agil_diff*5 + 50
            if percent_success > 80:
                percent_success = 80
            elif percent_success < 20:
                percent_success = 20
            roll_for_first_strike=libsigma.d100() 
            if roll_for_first_strike  <= percent_success:
                c.first_striker=c.combatant1
                c.second_striker=c.combatant2
            else:
                c.first_striker=c.combatant2 
                c.second_striker=c.combatant1            
            # end section
            
            c.combat_state=COMBAT_STATE_FIGHTING_C1_ACTION
            break 
        elif c.combat_state == COMBAT_STATE_FIGHTING_C1_ACTION:
            if c.first_striker == None:
                c.combat_state= COMBAT_STATE_FIGHTING_C2_ACTION
                break
            ## roll for hit -- Agilility
            agil_diff=c.first_striker.stats["agility"] - c.second_striker.stats["agility"]
            percent_success=agil_diff * 3 + 75
            
            if percent_success > 98:
                percent_success= 98
            elif percent_success < 40:
                percent_success= 40
            roll_for_hit=libsigma.d100()
            if roll_for_hit <= percent_success:
                #hit
                damage = calculate_damage(c.first_striker,c.second_striker) 
                libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor successfully $verb $direct for " + str(damage) +" damage!",c.first_striker,("hit","hits"),c.second_striker) 
                c.second_striker.HP=c.second_striker.HP - damage
                if c.second_striker.HP<= 0:
                    c.second_striker.HP=0
                    libsigma.report(libsigma.SELF | libsigma.ROOM, "$actor $verb victorious over $direct!",c.first_striker,("are","is"),c.second_striker)
                    world.combats.remove(c)
            else:
                #miss
                libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor $verb in an attempt to attack $direct!" ,c.first_striker,("miss","misses"),c.second_striker) 
           
            c.combat_state=COMBAT_STATE_FIGHTING_C2_ACTION
            break
        elif c.combat_state == COMBAT_STATE_FIGHTING_C2_ACTION:
            if c.first_striker == None:
                c.combat_state= COMBAT_STATE_FIGHTING_C1_ACTION
                break
            ## roll for hit -- Agilility
            agil_diff=c.second_striker.stats["agility"] - c.first_striker.stats["agility"]
            percent_success=agil_diff * 3 + 75
            
            if percent_success > 98:
                percent_success= 98
            elif percent_success < 40:
                percent_success= 40
            roll_for_hit=libsigma.d100()
            if roll_for_hit <= percent_success:
                #hit
                damage = calculate_damage(c.second_striker,c.first_striker) 
                libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor successfully $verb $direct for " + str(damage) +" damage!",c.second_striker,("hit","hits"),c.first_striker) 
                c.first_striker.HP=c.first_striker.HP - damage
                if c.first_striker.HP<= 0:
                    c.first_striker.HP=0
                    libsigma.report(libsigma.SELF | libsigma.ROOM, "$actor $verb victorious over $direct!",c.second_striker,("are","is"),c.first_striker)
                    world.combats.remove(c)
            else:
                #miss
                libsigma.report(libsigma.SELF | libsigma.ROOM,"$actor $verb in an attempt to attack $direct!" ,c.second_striker,("miss","misses"),c.first_striker) 
           
            c.combat_state=COMBAT_STATE_INTERMISSION
            break
        
        elif c.combat_state == COMBAT_STATE_INTERMISSION:
            agil_diff=c.combatant1.stats["agility"] - c.combatant2.stats["agility"]
            percent_success=agil_diff*5 + 50
            if percent_success > 80:
                percent_success = 80
            elif percent_success < 20:
                percent_success = 20
            roll_for_first_strike=libsigma.d100() 
            if roll_for_first_strike  <= percent_success:
                c.first_striker=c.combatant1
                c.second_striker=c.combatant2
            else:
                c.first_striker=c.combatant2 
                c.second_striker=c.combatant1            
            # end section
            c.combat_state=COMBAT_STATE_FIGHTING_C1_ACTION    
        
    return

def calculate_damage(attacker, defender):
    return attacker.stats["strength"]

def task_deinit():
    pass
