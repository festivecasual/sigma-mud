import handler
import libsigma
import creation
from archive import Archive
from world import World
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
                x = speaker.has_waits(function.priority)
                if not x:
                    libsigma.safe_mode(function, {
                          "speaker" : speaker,
                          "args" : tokens,
                          "message" : message,
                          "tail" : tail,
                          "mapped" : command
                          })
                else:
                    speaker.send_line("Please wait %d second%s." % (x, "s" if x!=1 else ""))
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
                speaker.state = STATE_CONFIG_NAME
            else:
                a = Archive()
                name = message.strip()
                if a.load(name, speaker):
                    speaker.state = STATE_PASSWORD
                else:
                    speaker.send_line("I do not know that name.", 2)

        elif speaker.state == STATE_PASSWORD:
            if check_password(message, speaker.password):
                # Do a dupe check to ensure no double logins
                # before entering STATE_PLAYING
                w = World()
                dupe = False
                for p in w.players:
                    if p.name == speaker.name:
                        dupe = True
                        speaker.send_line("That name is already active.", 2)
                        speaker.reset()
                        speaker.state = STATE_NAME
                        break

                if not dupe:
                    log("LOGIN", "User <%s> logged in at %s" % (speaker.name, time_string()))
                    speaker.state = STATE_PLAYING

                    # Add player to master players list
                    w.players.append(speaker)

                    # Insert player into default start room and "look"
                    libsigma.enter_room(speaker, w.rooms[options["default_start"]])
                    libsigma.report(libsigma.ROOM, "$actor has entered the game.", speaker)
                    speaker.send_line("", 2)
                    libsigma.queue_command(speaker, "look")
                    prompt = False

            else:
                speaker.send_line("Incorrect password.", 2)
                speaker.reset()
                speaker.state = STATE_NAME

        elif speaker.state == STATE_CONFIG_NAME:
            name = message.strip()
            a = Archive()
            if a.find(name):
                speaker.send_line("That name is already taken. Please choose another.", breaks=2)
            elif not valid_name(name):
                speaker.send_line("You cannot go by that name here.", breaks=2)
            else:
                speaker.name=name
                speaker.state=STATE_CONFIG_PASSWORD

        elif speaker.state == STATE_CONFIG_PASSWORD:
            if not valid_password(message):
                speaker.send_line("Please make your password at least five simple characters.", breaks=2)
            else:
                speaker.password = encrypt_password(message)
                speaker.state=STATE_CONFIG_CHAR
                creation.send_options(speaker)

        elif speaker.state == STATE_CONFIG_CHAR:
            if not creation.check_choice(speaker, message.lstrip()):
                speaker.send_line("Please make a valid choice.")
            if creation.is_configured(speaker):
                for stat in stats:
                    if speaker.stats[stat]==DEFAULT_STAT:
                        speaker.stats[stat]=3
                libsigma.add_points(speaker,5)

                speaker.state = STATE_PLAYING
                w = World()
                w.players.append(speaker)
                libsigma.enter_room(speaker, w.rooms[options["default_start"]])
                libsigma.report(libsigma.ROOM, "$actor has entered the game.", speaker)
                speaker.send_line("", 2)
                libsigma.queue_command(speaker, "look")
                speaker.HP=speaker.max_HP
            else:
                creation.send_options(speaker)

        elif speaker.state == STATE_PLAYING:
            if not run_command(speaker, message):
                speaker.send_line("What?")

        if speaker.socket and prompt:
            speaker.send_prompt()
