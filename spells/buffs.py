from magic import Spell,Incantation
from common import *
import libsigma
import random
from durations import Cooldown

class Adrenaline(Incantation):

    def cast(self,speaker,target):
        libsigma.report(libsigma.SELF | libsigma.ROOM, "$actor $verb slightly more agitated than before.",speaker,('appear','appears'))
        speaker.send_line("You have successfully cast Adrenaline!")
        pass


    def requirements_met(self,character,target):
        can_be_met,reason_not_met=super(Adrenaline,self).requirements_met(character,target)
        if target:
            can_be_met=False
            reason_not_met="You can't target anyone else with this spell!" 
        return can_be_met,reason_not_met


    def spell_cooldowns(self):
        return [Cooldown(["casting"],7)]