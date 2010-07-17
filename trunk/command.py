import archive
import world
import handler
import libsigma
import configplayer
import feats
from common import *


# Stores all commands pending processing, as a (speaker, message) tuple.
command_queue = []


def accept_command(speaker, message):
    command_queue.append((speaker, message))


def run_command(speaker, message):
    reduced = message.lstrip()
    if reduced:
        if reduced[0] == "'" and handler.specials["apostrophe"]:
            message = handler.specials["apostrophe"] + " " + reduced[1:]
        elif reduced[0] == ',' and handler.specials["comma"]:
            message = handler.specials["comma"] + " " + reduced[1:]
        elif reduced[0] == ':' and handler.specials["colon"]:
            message = handler.specials["colon"] + " " + reduced[1:]
        elif reduced[0] == '.' and handler.specials["period"]:
            message = handler.specials["period"] + " " + reduced[1:]
    else:
        return True

    try:
        tokens = message.lower().split()
    except:
        return False

    tail = message[(message.lower().find(tokens[0]) + len(tokens[0])):].lstrip()

    if len(tokens):
        for (command, function) in handler.mappings:
            if command.startswith(tokens[0]):
                x=speaker.has_waits(function.priority)
                if(not x):
                    libsigma.safe_mode(function, {
                                                  "speaker" : speaker,
                                                  "args" : tokens,
                                                  "message" : message,
                                                  "tail" : tail,
                                                  "mapped" : command        
                                                  })
                else:         
                    speaker.send_line("Please wait " + str(x) + " second" + ("s" if x!=1 else "") + ".")
                return True
        return False
    else:
        return True


def process_commands():
    while len(command_queue) > 0:
        speaker, message = command_queue.pop(0)
        prompt = True

        if speaker.state == STATE_NAME:
            if message.lower() == "new":
                speaker.state=STATE_CONFIG_NAME
            else:
                name = message.strip()
                player_file = archive.player_load(name)
                if player_file:
                    speaker.name = name
                    speaker.proto = player_file
                    speaker.state = STATE_PASSWORD
                else:
                    speaker.send_line("I do not know that name.", 2)

        elif speaker.state == STATE_PASSWORD:
            password = encrypt_password(message)

            if password == speaker.proto[0]:
                # Do a dupe check to ensure no double logins
                # before entering STATE_PLAYING
                dupe = False
                for check_player in world.players:
                    if check_player.name == speaker.name:
                        dupe = True
                        speaker.send_line("This name is already active.", 2)
                        speaker.name = None
                        speaker.proto = None
                        speaker.state = STATE_NAME
                        break

                if not dupe:
                    log("LOGIN", "User <%s> logged in at %s" % (
                            speaker.name, time_string()))

                    # Copy proto contents to main player class
                    try:
                        speaker.password = speaker.proto[0]
                        speaker.contents = speaker.proto[1]
                        speaker.worn_items = speaker.proto[2]
                        speaker.equipped_weapon = speaker.proto[3]
                        speaker.stats = speaker.proto[4]
                        speaker.points_to_allocate = speaker.proto[5]
                        speaker.gender = speaker.proto[6]
                        speaker.race = speaker.proto[7]
                        speaker.HP = speaker.proto[8]
                        
                        for s in speaker.proto[9]:
                            if feats.stances.has_key(s):
                                if not feats.stances[s].default: # handled by character class constructor
                                    speaker.stances.append(feats.stances[s])
                            else:
                                log("WARNING", "Couldn't load stance " + s + " for " + speaker.name +".")    
                        
                        for val in weapon_match_val:
                            if speaker.proto[10].has_key(val):
                                speaker.default_stance[val]=feats.stances[speaker.proto[10][val]]
                        
                        speaker.active_stance=feats.stances[speaker.proto[11]]
                        
                        
                    except IndexError:
                        log("WARNING", "Could not load entire player file for <" +speaker.name + ">")

                    # Add player to master players list
                    world.players.append(speaker)

                    # Insert player into default start room and "look"
                    libsigma.enter_room(speaker, world.rooms[options["default_start"]])
                    libsigma.report(libsigma.ROOM, "$actor has entered the game.", speaker)
                    speaker.send_line("", 2)
                    libsigma.queue_command(speaker, "look")
                    prompt = False

                    speaker.state = STATE_PLAYING
            else:
                speaker.send_line("Incorrect password.", 2)
                speaker.name = None
                speaker.proto = None
                speaker.state = STATE_NAME

        elif speaker.state == STATE_CONFIG_NAME:
            name = message.strip()
            player_file = archive.player_load(name)
            if player_file:
                speaker.send_line("This name is already taken. Please choose another.")
            else:
                speaker.name=name
                speaker.state=STATE_CONFIG_PASSWORD

        elif speaker.state == STATE_CONFIG_PASSWORD:
            speaker.password = encrypt_password(message)
            #world.players.append(speaker)
            #libsigma.enter_room(speaker, world.rooms[options["default_start"]])
            #libsigma.report(libsigma.ROOM, "$actor has entered the game.", speaker)
            #speaker.send_line("", 2)
            #libsigma.queue_command(speaker, "look")
            speaker.state=STATE_CONFIG_CHAR
            configplayer.send_options(speaker)
            prompt=True

        elif speaker.state == STATE_CONFIG_CHAR:
            if(not configplayer.check_choice(speaker, message.lstrip())):
                speaker.send_line("Please make a valid choice.")
            if(configplayer.is_configured(speaker)):
                for stat in stats:
                    if speaker.stats[stat]==DEFAULT_STAT:
                        speaker.stats[stat]=3
                libsigma.add_points(speaker,5)
                world.players.append(speaker)
                libsigma.enter_room(speaker, world.rooms[options["default_start"]])
                libsigma.report(libsigma.ROOM, "$actor has entered the game.", speaker)
                speaker.send_line("", 2)
                libsigma.queue_command(speaker, "look")
                speaker.HP=speaker.max_HP
                speaker.state = STATE_PLAYING
                prompt=True
            else:
                configplayer.send_options(speaker)

        elif speaker.state == STATE_PLAYING:
            if not run_command(speaker, message):
                speaker.send_line("What?")

        if speaker.socket and prompt:
            speaker.send_prompt()
