import time

from common import *


class Duration(object):
    def __init__(self):
        self.start_time=time.time()
        self.duration_in_secs=0
        self.infinite=False
    def remaining_time(self):
        if self.duration_in_secs==INFINITE:
            return INFINITE
        else:
            return max(self.duration_in_secs - int((time.time()-self.start_time)),0)

    def duration_expired(self):
        return (self.remaining_time()==0 and not self.infinite)


class Wait(Duration):
    def __init__(self, p,d):
        super(Wait, self).__init__()
        self.duration_in_secs=d
        self.priority=p

class Bonus(Duration):
    def __init__(self, stat,value,operator,context,source,type,d,condition):
        super(Bonus,self).__init__()
        self.stat=stat  # stat affected
        self.value=value # value of the stat affected
        self.operator=operator # MULTIPLICATIVE, ADDITIVE
        self.context=context # Either a value or list that explains when the Bonus is applied.
        self.source=source # id of the source of the Bonus.
        self.type=type # type of the object which creates the bonus. Types include worn, equipped, spell, effect
        self.bonus_duration=d # the possible duration of the bonus
        self.condition=condition # condition on which the bonus is applied.
        
    def set_duration(self,d):
        self.start_time=time.time()
        if d==INFINITE:
            self.infinite=True
            return
        else:
            self.duration_in_secs=int(d)
    
    def start_bonus_timer(self):
        self.set_duration(self.bonus_duration)
    
    def apply_bonus(self,stat_value):
        if self.operator=="+":
            return stat_value+self.value
        elif self.operator=="*":
            return stat_value*self.value
        log ("BONUS", "Bonus has incorrect 'operator' property. Returning default Statistic")
        return stat_value