import string

from libsigma import *
from world import *
from common import *


@handler
def time(data):
    speaker = data["speaker"]
    date_time = calendars[0].get_current_IG_DateTime()
    speaker.send_line( "It is "+ date_time["day_of_week"] +", the " + ordinals(date_time["day"]) + " of " + str(date_time["month"]) + ", " + str(date_time["year"]) + " years since the " + calendars[0].watershed_name + "." )
    speaker.send_line("It is " + string.zfill(date_time["hour"], 2) + ":" + string.zfill(date_time["minute"], 2) + ".")


@handler
def statistics(data):
    speaker = data["speaker"]
    for stat in stats:
        speaker.send_line(stat.capitalize()+ ": " + str(speaker.stats[stat]) )
    if speaker.points_to_allocate > 0:
        speaker.send_line("\r\nPoints not yet allocated: " + str(speaker.points_to_allocate))
    return


@handler
def health(data):
    speaker = data["speaker"]
    speaker.send_line("HP: " + str(speaker.HP) + "/" + str(speaker.max_HP))
    # more stuff about status affects to come


@handler
def allocate(data):
    speaker = data["speaker"]
    args =data ["args"]
    if len(args) < 2:
        speaker.send_line(str(args[0]).title() + " which stat?")
        return
    if len(args) > 4:
        speaker.send_line("Your command was not understood. Syntax is 'allocate <stat> <number>'")
        return
    alloc_am=0
    for s in stats:
        if s.startswith(str(args[1])):
            if len(args) == 2:
                alloc_am=1
            else:
                try:
                    alloc_am=int(args[2])
                except:
                    speaker.send_line("Please input a number to allocate your " + s + ".")
                    return
            if alloc_am <= speaker.points_to_allocate and alloc_am >=0:
                if raise_stat(speaker, s, alloc_am):
                    speaker.send_line("Your " + s + " has been increased by " +str(alloc_am) + ".")
                    remove_points(speaker,alloc_am)
                    return
                else:
                    speaker.send_line("You cannot increase your " + s + ".")
                    return
            else:
                speaker.send_line("You can't allocate that many points.")
                return
    speaker.send_line("Please indicate a valid stat to allocate.")
