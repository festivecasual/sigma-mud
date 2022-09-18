from common import *
from libsigma import *


@handler()
def say(data):
    speaker = data["speaker"]
    tail = data["tail"]

    report(SELF | ROOM, "$actor $verb, '" + tail + "'", speaker, ("say", "says"))


@handler()
def yell(data):
    speaker = data["speaker"]
    tail = data["tail"]

    report(SELF | ROOM, "$actor $verb, '" + tail + "'", speaker, ("yell", "yells"))
    report(NEAR, "You hear $actor $verb, '" + tail+ "'", speaker, ("yell", "yell"))


emote_mappings = {
        "cackle" : ("$actor $verb like a maniac!", "$actor $verb at $direct!", ("cackle", "cackles")),
        "grin" : ("$actor $verb.", "$actor $verb at $direct.", ("grin", "grins")),
        "laugh" : ("$actor $verb.", "$actor $verb at $direct.", ("laugh", "laughs")),
        "smile" : ("$actor $verb.", "$actor $verb at $direct.", ("smile", "smiles")),
        "slap" : ("", "$actor $verb $direct.", ("slap", "slaps")),
        "wave" : ("$actor $verb.", "$actor $verb at $direct.", ("wave", "waves")),
        "wink" : ("$actor $verb.", "$actor $verb at $direct.", ("wink", "winks")),
        "ponder" : ("$actor $verb an important question.", "", ("ponder", "ponders")),
        }


@handler()
def emote(data):
    speaker = data["speaker"]
    tail = data["tail"]
    mapped = data["mapped"]
    args = data["args"]

    if mapped == "emote":
        out = report(ROOM, "$actor " + tail + ".", speaker)
        speaker.send_line(out)
        return

    elif mapped in emote_mappings:
        nodirect, direct, verbs = emote_mappings[mapped]

        if len(args) > 1:
            if not direct:
                speaker.send_line("You can't do that.")
                return
            target = character_in_room(args[1], speaker.location, speaker)
            if target:
                report(SELF | ROOM, direct, speaker, verbs, target)
                return
            else:
                report(SELF, "They're not here.", speaker)
                return
        else:
            if nodirect:
                report(SELF | ROOM, nodirect, speaker, verbs)
                return
            else:
                report(SELF, "You must specify a target to $verb.", speaker, verbs)
                return

            alert("Emote command <" + mapped + "> does not have a usable form")
            return

    else:
        speaker.send_line("I don't understand.")
        alert("Emote command <" + mapped + "> references an unknown emote_mapping")


@handler()
def look(data):
    speaker = data["speaker"]
    args = data["args"]

    if len(args) > 1:
        objective = args[1]

        if objective == "self":
            speaker.send_line(speaker.desc)
            return

        direction = txt2dir(objective)
        if direction >= 0 and direction in open_exits(speaker.location):
            speaker.send_line("You see " + speaker.location.exits[direction].name + " in that direction.")
            return

        target = character_in_room(objective, speaker.location, speaker)
        if target:
            speaker.send_line(target.desc)
            return

        target = item_in_room(objective, speaker.location)
        if target:
            speaker.send_line(target.desc)
            return

        focus_text = focus_in_room(objective, speaker.location)
        if focus_text:
            speaker.send_line(focus_text)
            return

        speaker.send_line("You don't see that.")
        return

    speaker.send_line(speaker.location.name)
    speaker.send_line(speaker.location.desc)

    speaker.send("Exits: ")
    for code in open_exits(speaker.location):
        speaker.send(dir2txt(code) + " ")
    speaker.send_line("")

    for character in speaker.location.characters:
        if character != speaker and not character.hidden:
            speaker.send_line(character.short)

    for item in speaker.location.contents:
        speaker.send_line(item.short)


@handler(WALKING_PRIORITY)
def go(data):
    speaker = data["speaker"]
    args = data["args"]

    direction = -1
    if speaker.engaged:
        speaker.send_line("You can't do that, you're currently in combat!")
        return

    if "go".startswith(args[0]) and len(args) == 2:
        direction = txt2dir(args[1])
    elif len(args) == 1:
        direction = txt2dir(args[0])

    if direction == -1:
        speaker.send_line("Where do you want to go?")
    elif speaker.location.can_character_go(direction):
        if(speaker.hidden):
            run_command(speaker, "unhide")
        if speaker.location.altmsg[direction]!=None: # checks first for any alternate messaging
            report(ROOM, "$actor just went " + speaker.location.altmsg[direction]  + "." , speaker)
        elif dir2txt(direction) =="leave":
            report(ROOM, "$actor just went out.", speaker)
        elif dir2txt(direction) =="enter":
            report(ROOM, "$actor just went in.", speaker)
        else:
            report(ROOM, "$actor just went " + dir2txt(direction) + ".", speaker)
        enter_room(speaker, speaker.location.exits[direction])
        report(ROOM, "$actor has entered the room.", speaker)
        run_command(speaker, "look")
    else:
        speaker.send_line("There is no exit in that direction.")


@handler(WALKING_PRIORITY)
def get(data):
    speaker = data["speaker"]
    args = data["args"]

    if len(args) == 1:
        speaker.send_line(args[0].title() + " what?")
        return

    source = Sentence(args)
    result = source.ItemInRoom(speaker.location)

    if result.CompleteMatch():
        if 'stationary' in result[0].flags:
            speaker.send_line("You can't pick that up!")
            return

        transfer_item(result[0], speaker.location.contents, speaker.contents)
        report(SELF | ROOM, "$actor $verb $direct.", speaker, ("pick up", "picks up"), result[0])
    else:
        speaker.send_line("You can't find it.")


@handler(WALKING_PRIORITY)
def drop(data):
    speaker = data["speaker"]
    args = data["args"]

    if len(args) == 1:
        speaker.send_line("Drop what?")
        return
    elif len(args) != 2:
        speaker.send_line("You can't do that.")
        return

    for item in speaker.contents:
        for keyword in item.keywords:
            if keyword.startswith(args[1]):
                transfer_item(item, speaker.contents, speaker.location.contents)
                report(SELF | ROOM, "$actor $verb $direct.", speaker, ("drop", "drops"), item)
                return

    speaker.send_line("You don't have that.")


@handler()
def give(data):
    speaker = data["speaker"]
    args = data["args"]

    if len(args) < 2:
        speaker.send_line("Give what?")
        return
    elif len(args) < 3:
        speaker.send_line("Give to whom?")
        return

    source = Sentence(args)
    result = source.ItemInInventory(speaker).Allow('to').CharacterInRoom(speaker.location, speaker)

    if result.CompleteMatch():
        target, recipient = result

        if speaker == recipient:
            speaker.send_line("You already have it.")
        elif target in [o.transfer_item for o in recipient.offers]:
            speaker.send_line("You have already offered that to %s." % recipient.name)
        else:
            offer_item(target, speaker, recipient)
            report(SELF | ROOM, "$actor $verb $direct to $indirect.", speaker, ("offer", "offers"), target, recipient)
    elif not result[0]:
        speaker.send_line("You don't have that.")
    elif not result[1]:
        speaker.send_line("They're not here.")
    else:
        speaker.send_line("You can't do that.")


@handler()
def accept(data):
    speaker = data["speaker"]
    args = data["args"]
    tail = data["tail"]
    mapped = data["mapped"]

    if len(speaker.offers) == 0:
        speaker.send_line("You have not been offered anything recently.")
        return
    elif len(speaker.offers) == 1:
        offer = speaker.offers[0]
    else:
        offer = None
        for search in speaker.offers:
            for keyword in search.transfer_item.keywords:
                if tail and keyword.startswith(tail):
                    offer = search

    if not offer or len(args) == 0:
        speaker.send_line("Current offers:")
        for o in speaker.offers:
            speaker.send_line("    %s (from %s)" % (o.transfer_item.name, o.from_character.name))
        return

    if not offer.check_valid():
        offer.dequeue()
        return

    offer.to_character.offers.remove(offer)

    if mapped == "accept":
        transfer_item(offer.transfer_item, offer.from_character.contents, offer.to_character.contents)
        report(
                SELF | ROOM,
                "$actor $verb $direct from $indirect.",
                speaker,
                ("accept", "accepts"),
                offer.transfer_item,
                offer.from_character
                )
    else:
        report(
                SELF | ROOM,
                "$actor $verb $direct from $indirect.",
                speaker,
                ("refuse", "refuses"),
                offer.transfer_item,
                offer.from_character
                )


@handler()
def inventory(data):
    speaker = data["speaker"]

    speaker.send_line("You are carrying:")
    if len(speaker.contents):
        for item in speaker.contents:
            speaker.send_line("    " + item.name + ("" if not item.stackable else (" x " + str(item.quantity))))
    else:
        speaker.send_line("    nothing")

    speaker.send_line("You are wearing:")
    if len(speaker.worn_items):
        for i in speaker.worn_items:
            speaker.send_line("    " + i.name)
    else:
        speaker.send_line("    nothing")

    speaker.send_line("You have equipped:")
    if len(speaker.equipped_weapon) > 0:
        for j in speaker.equipped_weapon:
            speaker.send_line("    " + j.name+ ("" if not j.stackable else (" x " + str(j.quantity))))
    else:
        speaker.send_line("    nothing")


@handler()
def open(data):
    speaker=data["speaker"]
    args=data["args"]

    if len(args) < 2:
        speaker.send_line(str(args[0]).title() + " what?")
    else:  #TODO: support currently only for doors! Open will most likely also deal with containers later
        direction=txt2dir(args[1])
        if(speaker.location.is_door_closed(direction)):
            speaker.location.open_door(direction)
            report(SELF | ROOM, "$actor $verb the door.", speaker, ("open","opens"))
            announce(ROOM, speaker.location.exits[direction],"The door opens.")
        else:
            speaker.send_line("You can't open that.")


@handler()
def close(data):
    speaker=data["speaker"]
    args=data["args"]

    if len(args) < 2:
        speaker.send_line(str(args[0]).title() + " what?")
    else: #TODO: support currently only for doors! Close will most likely also deal with containers later
        direction=txt2dir(args[1])
        if(not speaker.location.is_door_closed(direction) and speaker.location.doors[direction]!=None and direction !=-1):
            speaker.location.close_door(direction)
            report(SELF | ROOM, "$actor $verb the door.", speaker, ("close","closes"))
            announce(ROOM, speaker.location.exits[direction],"The door closes shut.")
        else:
            speaker.send_line("You can't close that.")


@handler(WALKING_PRIORITY)
def wear(data):
    speaker=data["speaker"]
    args=data["args"]

    if len(args) < 2:
        speaker.send_line(str(args[0]).title() + " what?")
        return
    for item in speaker.contents:
        for keyword in item.keywords:
            if keyword.startswith(args[1]):
                if not item.wearable:
                    speaker.send_line("You can't wear that.")
                    return
                if at_capacity(speaker, item.wearable.worn_position):
                    speaker.send_line("You can't wear anything else on your %s." % item.wearable.worn_position)
                    return
                report(SELF | ROOM, "$actor $verb on %s." % item.name, speaker, ("put","puts"))
                transfer_item(item, speaker.contents,speaker.worn_items)
                speaker.reference_bonuses(item.wearable.bonuses,'auto')


                return

    speaker.send_line("You don't have anything like that in your inventory.")


@handler(WALKING_PRIORITY)
def remove(data): #TODO: does not take into account capacity of the character yet. Still work to do.
    speaker=data["speaker"]
    args=data["args"]
    if len(args) < 2:
        speaker.send_line(str(args[0]).title() + " what?")
        return
    for item in speaker.worn_items:
        for keyword in item.keywords:
            if keyword.startswith(args[1]):
                report(SELF | ROOM, "$actor $verb " + item.name + ".", speaker, ("remove", "removes" ))
                transfer_item(item,speaker.worn_items,speaker.contents)
                speaker.dereference_bonuses(item.id)
                return

    speaker.send_line("You're not wearing anything like that.       ")


@handler()
def equip(data):
    speaker=data["speaker"]
    args=data["args"]
    if len(args) < 2:
        speaker.send_line(str(args[0]).title() + " what?")
        return
    for item in speaker.contents:
        for keyword in item.keywords:
            if keyword.startswith(args[1]):
                if not item.weapon and not item.ammo:
                    speaker.send_line("You can't wield that.")
                    return
                if item.ammo:
                    if len(speaker.equipped_weapon)>1:
                        speaker.send_line("You can't wield anything else.")
                        return
                    elif len(speaker.equipped_weapon)<1:
                        speaker.send_line("You must have a proper weapon equipped before equipping this." )
                        return
                    elif item.ammo.ammo_type==ammo_requirements[speaker.equipped_weapon[0].weapon.weapon_type]:
                        transfer_item(item, speaker.contents, speaker.equipped_weapon)
                        report(SELF | ROOM, "$actor $verb " + item.name + ".", speaker, ("wield", "wields" ))
                        return
                    else:
                        speaker.send_line("You must have an proper weapon equipped before equipping this.")
                    return

                if len(speaker.equipped_weapon)==1: ## Editable for future multi-weapon equipping abilities
                    speaker.send_line("You can't wield anything else.")
                    return
                if not speaker.can_equip(item.weapon.weapon_type):
                    speaker.send_line("You can't wield a weapon like that!")
                    return
                transfer_item(item, speaker.contents, speaker.equipped_weapon)
                speaker.active_stance=speaker.default_stance[item.weapon.weapon_type]
                report(SELF | ROOM, "$actor $verb " + item.name + ".", speaker, ("wield", "wields" ))
                speaker.send_line("You are now using the " + speaker.active_stance.name.capitalize() + " stance.")
                for c in speaker.combats:
                    c.in_range_set_action()
                return
    speaker.send_line("You don't have anything like that in your inventory.")
    return


@handler()
def unequip(data):
    speaker=data["speaker"]
    args=data["args"]
    if len(args) < 2:
        speaker.send_line(str(args[0]).title() + " what?")
        return
    for item in speaker.equipped_weapon:
        for keyword in item.keywords:
            if keyword.startswith(args[1]):
                report(SELF | ROOM, "$actor $verb " + item.name + ".", speaker, ("unequip", "unequips" ))
                transfer_item(item,speaker.equipped_weapon,speaker.contents)

                for i2 in speaker.equipped_weapon:
                    if i2.ammo:
                        if ammo_requirements[item.weapon.weapon_type] == i2.ammo.ammo_type:
                            run_command(speaker, args[0] + " " + i2.name)

                if item.weapon:
                    for c in speaker.combats:
                        c.in_range_set_action(speaker)
                    speaker.active_stance=speaker.default_stance['bare handed']
                    speaker.send_line("You are now using the " + speaker.active_stance.name.capitalize() + " stance.")
                return

    speaker.send_line("You're not wielding anything like that.")


@handler()
def count(data):
    speaker = data["speaker"]
    args = data["args"]

    if len(args) == 1:
        speaker.send_line(args[0].title() + " what?")
        return

    source = Sentence(args)
    result = source.ItemInRoom(speaker.location)

    if result.CompleteMatch():
        stri="You see that there "
        if result[0].quantity > 1:
            stri+=("are " + str(result[0].quantity) + " of ")
        else:
            stri+="is one of "
        stri+=(result[0].name + ".")
        speaker.send_line(stri)
    else:
        speaker.send_line("You can't find it.")


@handler(WALKING_PRIORITY)
def search(data):
    pass


@handler(WALKING_PRIORITY)
def reveal(data):
    pass
