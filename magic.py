import libsigma
from world import World
from common import *

class Spell (object):
    def blank_spell(self):
        self.name=''
        self.abbreviation=[]
        self.difficulty=0
        self.desc=''
        self.cost=0
        self.sigils_required=[]
        self.range=MELEE_RANGE
        self.area_of_effect=0
        self.speed=SPELL_SPEED_INSTANT
        self.type=SPELL_TYPE_UNCONTESTED
        #self.function = None
        self.cooldown=0
        self.bonuses=[]

    def __init__(self,node=None):
        self.blank_spell()
        self.area=[]
        self.name=required_child(node,'name').text
        self.cost=int(required_child(node,'cost').text)
        self.difficulty=int(required_child(node,'difficulty').text)
        for child in node.findall('area'):
            self.area.append(child.text)
        self.type=required_child(node,'type').text
        self.speed=required_child(node,'speed').text
        #self.spell=required_child(node,'function').text
        self.cooldown=int(required_child(node,'cooldown').text)
        self.convert_text_to_types()
        for abrev in node.findall('abbreviation'):
            self.abbreviation.append(strip_whitespace(abrev.text))

    def convert_text_to_types(self):
        value_speed_tuple=(SPELL_SPEED_INSTANT,SPELL_SPEED_INCANTATION)
        text_speed_tuple=('instant','incantation')
        text_area_tuple=('room','area','game')
        value_area_tuple=(libsigma.ROOM,libsigma.AREA,libsigma.GAME)
        value_type_tuple=(SPELL_TYPE_UNCONTESTED,SPELL_TYPE_COMBAT,SPELL_TYPE_CONTESTED)
        text_type_tuple=('uncontested','combat','contested')
        self.speed=libsigma.txt2val(self.speed,text_speed_tuple,value_speed_tuple)
        self.type=libsigma.txt2val(self.type,text_type_tuple,value_type_tuple)

        for value in self.area:
            self.area_of_effect+=libsigma.txt2val(value,text_area_tuple,value_area_tuple)

    def cast(self, speaker,target):
        """
            This will be written by any class that inherits from spell. This is the
            method that represents what happens when the spell is successfully cast
            after it passes all requirements for casting
        """
        pass

    def requirements_met(self,character,target):
        can_be_met=character.MP >= self.cost
        reason_not_met="" if can_be_met else "You don't have enough MP to cast this spell!"
        if can_be_met:
            r = character.has_cooldowns()
            if r:
                can_be_met=False
                reason_not_met="You must wait " + str (r) + " seconds before casting " + self.name + "."

        return can_be_met,reason_not_met
    
    def remove_resources(self,character):
        character.MP -= self.cost

    def applicable_bonuses(self):
        return ["casting"]

    def spell_cooldowns(self):
        return []

class Incantation(Spell):
    def __init__(self,node=None):
        self.blank_spell()
        super(Incantation,self).__init__(node)

    def requirements_met(self,character,target):
        can_be_met,reason_not_met=super(Incantation,self).requirements_met(character,target)
        if character.spell_chanting==self:
            if not character.spell_chanting_complete:
                can_be_met=False
                reason_not_met="You have not completed chanting " +self.name + "!"

        if not character.spell_chanting:
            can_be_met=False
            reason_not_met="You must chant this spell before you can cast it."

        return can_be_met,reason_not_met

    def chant(self,character):
        character.spell_chanting=self
        libsigma.insert_task('chant_' + character.name + '_' + self.name,character.finish_chanting, 12, 1)


    def remove_resources(self,character):
        super(Incantation,self).remove_resources(character)
        character.spell_chanting=None
        character.spell_chanting_finished=False