from common import *


def send_options(speaker):
    if speaker.gender == GENDER_NEUTRAL:
        speaker.send_line()
        speaker.send_line("Please choose your gender:")
        for o in genders[1:]:
            speaker.send_line('%d) %s' % (genders.index(o), o))
    elif speaker.race == RACE_NEUTRAL:
        speaker.send_line()
        speaker.send_line("Please choose your race:")
        for o in races[1:]:
            speaker.send_line('%d) %s' % (races.index(o), o))


def check_choice(speaker, message):
    option=0
    try:
        option=int(message)
    except ValueError:
        return False

    if speaker.gender==GENDER_NEUTRAL:
        if 0 < option < len(genders):
            try:
                speaker.gender=genders[option]
            except IndexError:
                speaker.gender=GENDER_NEUTRAL
                return False
            return True
        else:
            return False

    if speaker.race==RACE_NEUTRAL:
        if 0 < option < len(races):
            try:
                speaker.race=races[option]
            except IndexError:
                speaker.race=RACE_NEUTRAL
                return False
            return True
        else:
            return False

    return False


def is_configured(speaker):
    return speaker.gender != GENDER_NEUTRAL and speaker.race != RACE_NEUTRAL


class Class(object):
    def __init__(self, node):
        self.name = strip_whitespace(required_child(node, 'name').text)
        self.desc = wordwrap(strip_whitespace(required_child(node, 'desc').text))
        self.background = wordwrap(strip_whitespace(required_child(node, 'background').text))
        # TODO 'stats' 'paths' 'skills'
