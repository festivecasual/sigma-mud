from libsigma import *
from world import *

@handler
def time(data):
    speaker = data["speaker"]
    speaker.send_line(calendars[0].get_current_IG_DateTime())
