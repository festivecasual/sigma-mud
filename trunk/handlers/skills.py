from libsigma import *
import world




@handler(WALKING_PRIORITY)
def hide(data):
    speaker = data["speaker"]
    args = data["args"]
    
    if (len(args) > 1):
        speaker.send_line("You can't do that.")
        return
    if (speaker.hidden):
        speaker.send_line("You're already hidden!")
        return
    else:
        speaker.send_line("You look around for a moment, and find a hiding place.")
        for c in speaker.location.characters:
            if(c!=speaker):
                if(roll_for_success(c.stats["perception"],speaker.stats["charisma"]*.25 + speaker.stats["agility"]*.75, 0, 100,4,50)):
                    c.send_line("You glance at " + speaker.name + " finding a hiding spot.")
        speaker.hidden=True
        speaker.add_wait(hide.priority,5)
    return

@handler(WALKING_PRIORITY)
def unhide(data):
    
    speaker = data["speaker"]
    args = data["args"]
    
    if (len(args) > 1):
        speaker.send_line("You can't do that.")
        return
    if(not speaker.hidden):
        speaker.send_line("You're already in plain view!")
        return
    else:
        report(SELF | ROOM, "$actor $verb $direct, stepping out of a hiding place." , speaker, ("reveal", "reveals"), speaker)
        speaker.hidden=False
    return

@handler(WALKING_PRIORITY)
def assess(data):
    speaker=data["speaker"]

   
    if speaker.combats:
        for c in speaker.combats:
            other_guy=c.combatant1.name if c.combatant1!=speaker else c.combatant2.name
            if c.combat_state==COMBAT_STATE_INITIALIZING or c.combat_state==COMBAT_STATE_INITIALIZING:
                speaker.send_line("You are in combat, but not yet engaged at a range with " + other_guy +".")
                return
            if c==speaker.engaged:           
                speaker.send_line("You are engaged at " + val2txt(c.range,range_match_val,range_match_txt) + " with " + other_guy + ".")
            else:
                speaker.send_line(other_guy + " is at " + val2txt(c.range,range_match_val,range_match_txt) + " range with you.")
    else:
        speaker.send_line("You are not in combat!")