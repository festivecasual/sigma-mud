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
