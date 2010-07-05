import string

from libsigma import *
from world import *
#from common import *


@handler()
def time(data):
    speaker = data["speaker"]
    date_time = calendars[0].get_current_IG_DateTime()
    speaker.send_line( "It is "+ date_time["day_of_week"] +", the " + ordinals(date_time["day"]) + " of " + str(date_time["month"]) + ", " + str(date_time["year"]) + " years since the " + calendars[0].watershed_name + "." )
    speaker.send_line("It is " + string.zfill(date_time["hour"], 2) + ":" + string.zfill(date_time["minute"], 2) + ".")


@handler()
def statistics(data):
    speaker = data["speaker"]
    for stat in stats:
        speaker.send_line(stat.capitalize()+ ": " + str(speaker.stats[stat]) )
    if speaker.points_to_allocate > 0:
        speaker.send_line("\r\nPoints not yet allocated: " + str(speaker.points_to_allocate))
    return


@handler()
def health(data):
    speaker = data["speaker"]
    speaker.send_line("HP: " + str(speaker.HP) + "/" + str(speaker.max_HP))
    # more stuff about status affects to come


@handler()
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

@handler()
def stance(data):
    speaker = data["speaker"]
    args=data["args"]
    
    
    if len(args) ==1:
        output_list=[]
        speaker.send_line("STANCES:")
        for s in speaker.stances:
            strin=val2txt(s.weapon_type,weapon_match_val,weapon_match_txt).capitalize()
            strin=strin+ ":\t\t " + s.name.capitalize()
            if speaker.default_stance[s.weapon_type]==s:
                strin=strin+"*"
            if speaker.active_stance==s:
                strin=strin+"+"
            output_list.append(strin)
        output_list.sort()
        for stan in output_list:
            speaker.send_line(stan)
        speaker.send_line("* denotes a default stance.")
        speaker.send_line("+ denotes your current stance.")
    elif len(args)<=3:
        if "help".startswith(args[1]):
            speaker.send_line("STANCE USAGE")
            speaker.send_line("STANCE -- provides a list of stances you have learned")
            speaker.send_line("STANCE DEFAUlT <stance name> -- sets a given stance to default. One default for each weapon type is possible")
            speaker.send_line("STANCE CHOOSE <stance name> -- sets your active stance to a given stance")
            return
        elif "default".startswith(args[1]):
            if len(args)<3:
                speaker.send_line("Which stance do you want as your default?")
                speaker.send_line("(Type STANCE HELP for usage.)")
                return
            for n in speaker.stances:
                if n.name.startswith(args[2]):
                    speaker.default_stance[n.weapon_type]=n
                    speaker.send_line("Your default " + val2txt(n.weapon_type,weapon_match_val,weapon_match_txt) + " stance is now set to " + n.name.capitalize() + ".")
                    return
            speaker.send_line("You don't have a stance like that.")
        elif "choose".startswith(args[1]):
            if len(args)<3:
                speaker.send_line("Which stance do you wish to use?")
                speaker.send_line("(Type STANCE HELP for usage.)")
                return
            active_weapon_type=BARE_HAND
            if len(speaker.equipped_weapon)>0: # assumes that equipped weapons all have to be the same type
                active_weapon_type=speaker.equipped_weapon[0].weapon_type
            for n in speaker.stances:
                if n.name.startswith(args[2]):
                    if(n.weapon_type !=active_weapon_type):
                        speaker.send_line("You must choose a stance with the same weapon type as your equipped weapon(" + val2txt(active_weapon_type,weapon_match_val,weapon_match_txt).capitalize() + ")." )
                        return
                    speaker.active_stance=n
                    speaker.send_line("Your stance is now set to " + n.name + ".")
                    return            
        else:
            speaker.send_line("STANCE " + str(args[1]) + " is not a valid option")
            speaker.send_line("(Type STANCE HELP for usage.)")
            return
        

    return