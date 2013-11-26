from magic import Spell
from common import *
import libsigma
import random
from durations import Cooldown

class Heal(Spell):

    def cast(self,speaker,target):
        target= speaker if not target else target
        intel=speaker.effective_stat("intelligence",self.applicable_bonuses())
        disc=int(speaker.effective_stat("discipline",self.applicable_bonuses()) * .75)
        value=int(min((5+disc) + random.randint(0,intel),45))
        target.HP+=value 
        libsigma.report(libsigma.SELF | libsigma.ROOM, "A faint aura washes over $actor!",target)
        target.send_line("You have gained " + str(value) +" HP!")
        pass


    def applicable_bonuses(self):
        bonuses=[]
        bonuses.extend(super(Heal,self).applicable_bonuses())
        bonuses.append("healing_spell")
        return bonuses

    def spell_cooldowns(self):
        return [Cooldown(["healing_spell"],5)]