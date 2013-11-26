from common import *
from libsigma import *

@handler()
def cast(data):
    speaker=data["speaker"]
    args=data["args"]
    spell_ref=None
    spell_target=None
    target=None
    if len(args) > 2:
        spell_target=args[2]
        target = character_in_room(spell_target, speaker.location, speaker) #TODO: Make this generalized so a target could be a character, object, etc
    if len (args) > 1:
        spell_ref=args[1]

    #Does the speaker know the spell?
    spell=speaker.has_spell(spell_ref)
    if not spell:
        speaker.send_line("You do not know that spell.")
        return
    #Can the speaker cast the spell?
    can_cast,reason=speaker.can_cast_spell(spell,target)
    if not can_cast:
        speaker.send_line(reason)
    #If the speaker can cast, then remove resources, and then cast
    else:
        if spell_target:
            report(SELF | ROOM,"$actor $verb at $direct.", speaker, ("gesture","gestures"),target)
        else:
            report(SELF | ROOM,"$actor $verb.", speaker, ("gesture","gestures"))
        spell.remove_resources(speaker)
        spell.cast(speaker,target)
        speaker.cooldowns.extend(spell.spell_cooldowns())

@handler()
def chant(data):
    speaker=data["speaker"]
    args=data["args"]
    spell_ref = None
    if len (args) > 1:
        spell_ref=args[1]

    spell=speaker.has_spell(spell_ref)
    if not spell:
        speaker.send_line("You do not know that spell.")
        return
    if not hasattr(spell,'chant'):
        speaker.send_line("You can't chant that spell!")
        return
    if speaker.spell_chanting !=None:
        if speaker.spell_chanting==spell:
            speaker.send_line("You are already chanting " + spell.name + "!")
            return
        else:
            speaker.send_line("You are already chanting another spell!")
    spell.chant(speaker)
    report(SELF | ROOM, "$actor $verb chanting a spell.", speaker,('begin','begins'))


    