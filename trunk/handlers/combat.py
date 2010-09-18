from libsigma import *
from world import World
from combat import Combat


@handler()
def engage(data):
    #first argument should be person/character
    speaker=data["speaker"]
    args=data["args"]
    command=data["mapped"]

    if len(args) < 2:
        speaker.send_line(command.title() + " what?")
        return

    engagee = character_in_room(args[1], speaker.location, speaker)
    if not engagee:
        speaker.send_line("They're not here.")
        return

    if engagee == speaker:
        speaker.send_line("You cannot initiate combat with yourself.")
        return

    for flag in engagee.flags:
        if (flag=="peaceful"):
            speaker.send_line("You can't attack that!")
            return

    if speaker.engaged:
        if speaker.engaged.combatant1==engagee or speaker.engaged.combatant2==engagee:
            speaker.send_line("You are already engaged in combat with " + engagee.name + "!" )
        else:
            for co in speaker.combats:
                if  co.combatant1==engagee or co.combatant2==engagee:
                    speaker.send_line("You turn your attention toward " + engagee.name + "!")
                    report(ROOM, "$actor $verb " + pronoun_possessive[speaker.gender] + " attention toward $direct!", speaker, ("turn", "turns"), engagee)
                    speaker.engaged=co
                    for co2 in speaker.combats:
                        co2.in_range_set_action()
                    return
            speaker.send_line("You are too busy to fight anything else!")

        return

    w = World()
    c = Combat(speaker,engagee)
    w.combats.append(c)
    speaker.combats.append(c)
    engagee.combats.append(c)
    report(SELF | ROOM,"$actor $verb ready to engage $direct in combat!",speaker,("appear", "appears"),engagee)
    return


@handler(WALKING_PRIORITY)
def advance(data):
    args=data["args"]
    speaker=data["speaker"]
    pwr=None

    if len(args) > 2:
        speaker.send_line("I don't understand.")
        return

    if not speaker.engaged:
        speaker.send_line("But you're not in combat!")
        return

    if len(args) == 2:
        for range in range_match_txt:
            if range.startswith(args[1]):
                pwr=txt2val(range,range_match_txt,range_match_val)
                break
        if not pwr:
            speaker.send_line(args[1].capitalize() + " is not a range.")
            return

    if not pwr:
        pwr = preferred_range['bare handed' if not speaker.equipped_weapon else speaker.equipped_weapon[0].weapon.weapon_type]

    if pwr >= speaker.engaged.range:
        speaker.send_line("You can't advance, you are already at " + val2txt(speaker.engaged.range,range_match_val,range_match_txt) + " range with " + (speaker.engaged.combatant1.name if speaker.engaged.combatant1 != speaker else speaker.engaged.combatant2.name) + "!" )
        return

    speaker.engaged.set_override_range(speaker,pwr)
    speaker.engaged.set_action(speaker,COMBAT_ACTION_ADVANCING)

    speaker.send_line("You will attempt to advance upon " + (speaker.engaged.combatant1.name if speaker.engaged.combatant1 != speaker else speaker.engaged.combatant2.name) + " at the next opportunity.")


@handler(WALKING_PRIORITY)
def withdraw(data):
    args=data["args"]
    speaker=data["speaker"]
    pwr=None

    if len(args) > 2:
        speaker.send_line("I don't understand.")
        return

    if not speaker.engaged:
        speaker.send_line("But you're not in combat!")
        return

    if len(args) == 2:
        for range in range_match_txt:
            if range.startswith(args[1]):
                pwr=txt2val(range,range_match_txt,range_match_val)
                break
        if not pwr:
            speaker.send_line(args[1].capitalize() + " is not a range.")
            return

    if not pwr:
        pwr = preferred_range['bare handed' if not speaker.equipped_weapon else speaker.equipped_weapon[0].weapon.weapon_type]

    if pwr <= speaker.engaged.range:
        speaker.send_line("You can't withdraw, you are already at " + val2txt(speaker.engaged.range,range_match_val,range_match_txt) + " range with " + (speaker.engaged.combatant1.name if speaker.engaged.combatant1 != speaker else speaker.engaged.combatant2.name) + "!" )
        return

    speaker.engaged.set_override_range(speaker,pwr)
    speaker.engaged.set_action(speaker,COMBAT_ACTION_WITHDRAWING)

    speaker.send_line("You will attempt to withdraw from " + (speaker.engaged.combatant1.name if speaker.engaged.combatant1 != speaker else speaker.engaged.combatant2.name) + " at the next opportunity.")


@handler(WALKING_PRIORITY)
def retreat(data):
    speaker=data["speaker"]
    args=data["args"]
    direction=None
    if not speaker.engaged:
        speaker.send_line("But you're not in combat!")
        return
    if len(args)>2:
        speaker.send_line("I don't understand.")
        return
    if len(args)==2:
        direction = txt2dir(args[1])
        if not (direction in speaker.location.exits):
            direction=None
    speaker.engaged.set_retreat(speaker,direction)
    speaker.send_line("You will attempt to retreat at your next opportunity")


@handler(WALKING_PRIORITY)
def loot(data):
    speaker = data["speaker"]
    args = data["args"]

    if len(args) == 1:
        speaker.send_line(args[0].title() + " what?")
        return

    source = Sentence(args)
    result = source.ItemInRoom(speaker.location)

    if result.CompleteMatch():
        if 'lootable' in result[0].flags:
            item_looted=result[0]
            speaker.send_line("You loot " + item_looted.name + "..." )
            if item_looted.money:
                speaker.send_line("...and you find " + str(item_looted.money) +  " " +  options["currency"] + "s!")
                transfer_money(item_looted.money,item_looted,speaker)
            else:
                speaker.send_line("...and find nothing special.")
            speaker.location.contents.remove(item_looted)
            del w.items[item_looted.id]
            return
        else:
            speaker.send_line("You can't loot that!")
