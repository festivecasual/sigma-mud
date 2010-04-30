from libsigma import *
#import world




@handler
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
    return

@handler
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