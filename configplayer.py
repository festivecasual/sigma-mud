from common import *


def send_options(speaker):
    if(speaker.gender == GENDER_NEUTRAL):
        speaker.send("\r\nPlease choose your gender:\r\n")
        for o in gender:
            if o !=GENDER_NEUTRAL:
                speaker.send(str(gender.index(o)) + ") "     +o + "\r\n")
    elif(speaker.race == RACE_NEUTRAL):
        speaker.send("\r\nPlease choose your race:\r\n")
        for o in races:
            if o !=RACE_NEUTRAL:
                speaker.send(str(races.index(o)) + ") "     +o + "\r\n")


def check_choice(speaker, message):
    option=0
    try:
        option=int(message)
    except:
        return False
    if(speaker.gender == GENDER_NEUTRAL):
        if option==GENDER_NEUTRAL:
            return False
        try:
            speaker.gender= gender[option]
        except IndexError:
            speaker.gender=GENDER_NEUTRAL
            return False
        return True
    if(speaker.race == RACE_NEUTRAL):
        if option==RACE_NEUTRAL:
            return False
        try:
            speaker.race= races[option]
        except IndexError:
            speaker.race=RACE_NEUTRAL
            return False
        return True
    return False


def is_configured(speaker):
    if speaker.gender == GENDER_NEUTRAL or speaker.race == RACE_NEUTRAL:
        return False
    return True
