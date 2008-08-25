from libsigma import *
from world import *
from common import *

@handler
def time(data):
    speaker = data["speaker"]
    date_time = calendars[0].get_current_IG_DateTime()
    speaker.send_line( "It is "+ date_time["day_of_week"] +", the " + ordinals(date_time["day"]) + " of " + str(date_time["month"]) + ", " + str(date_time["year"]) + " years since the " + calendars[0].watershed_name + "." )
    speaker.send_line("It is " + str(date_time["hour"]) + ":" + str(date_time["minute"]) + ".")