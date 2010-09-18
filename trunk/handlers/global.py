import string

from libsigma import *
from common import *
from world import World


@handler()
def time(data):
    speaker = data["speaker"]
    w = World()
    date_time = w.calendars[0].get_current_IG_DateTime()
    speaker.send_line("It is %s, the %s of %s, %d year%s since the %s." % (date_time["day_of_week"], ordinals(date_time["day"]), date_time["month"], date_time["year"], 's' if date_time["year"] != 1 else '', w.calendars[0].watershed_name))
    speaker.send_line("It is %02d:%02d." % (date_time["hour"], date_time["minute"]))


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
    args = data["args"]
    mapped = data["mapped"]
    if len(args) < 2:
        speaker.send_line(mapped.title() + " which stat?")
        return
    if len(args) > 3:
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
    args = data["args"]

    source = Sentence(args)

    if source.Complete():
        output_list = []
        speaker.send_line("STANCES:")
        for s in speaker.stances:
            #TODO: Needs to use new table function
            strin = s.weapon_type.capitalize() + ":\t\t " + s.name.capitalize()
            if speaker.default_stance[s.weapon_type]==s:
                strin += "*"
            if speaker.active_stance==s:
                strin += "+"
            output_list.append(strin)
        output_list.sort()
        for stan in output_list:
            speaker.send_line(stan)
        speaker.send_line("* denotes a default stance.")
        speaker.send_line("+ denotes your current stance.")
        return

    if source.Keyword("help").CompleteMatch():
        speaker.send_line("STANCE USAGE")
        speaker.send_line("STANCE -- provides a list of stances you have learned")
        speaker.send_line("STANCE DEFAULT <stance name> -- sets a given stance to default. One default")
        speaker.send_line("    for each weapon type is possible")
        speaker.send_line("STANCE CHOOSE <stance name> -- sets your active stance to a given stance")
        return

    default = source.Keyword("default")
    if default.CompleteMatch():
        speaker.send_line("Which stance do you want as your default?")
        speaker.send_line("(Type STANCE HELP for usage.)")
        return
    if default.Literal().CompleteMatch():
        for n in speaker.stances:
            if default.Keyword(n.name).CompleteMatch():
                speaker.default_stance[n.weapon_type] = n
                speaker.send_line("Your default %s stance is now set to %s." % (n.weapon_type, n.name.capitalize()))
                return
        speaker.send_line("You don't have a stance like that.")
        return

    choose = source.Keyword("choose")
    if choose.CompleteMatch():
        speaker.send_line("Which stance do you wish to use?")
        speaker.send_line("(Type STANCE HELP for usage.)")
        return
    if choose.Literal().CompleteMatch():
        active_weapon_type='bare handed'
        if len(speaker.equipped_weapon)>0:  # assumes that equipped weapons all have to be the same type
            active_weapon_type=speaker.equipped_weapon[0].weapon.weapon_type
        for n in speaker.stances:
            if choose.Keyword(n.name).CompleteMatch():
                if n.weapon_type != active_weapon_type:
                    speaker.send_line("You must choose a stance with the same weapon type as your equipped weapon (" + active_weapon_type.capitalize() + ").")
                    return
                speaker.active_stance = n
                speaker.send_line("Your stance is now set to " + n.name + ".")
                return
        speaker.send_line("You don't have a stance like that.")
        return

    speaker.send_line("That is not a valid usage for STANCE.")
    speaker.send_line("(Type STANCE HELP for usage.)")


@handler()
def wealth(data):
    speaker=data["speaker"]
    if not speaker.money:
        speaker.send_line("You are carrying no money.")
    else:
        speaker.send_line("You currently have " + str(speaker.money) + " " + options["currency"] +"s.")
