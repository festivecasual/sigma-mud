import datetime

from common import *
from functools import reduce


class Calendar(object):
    def __init__(self, node, cname):
        self.name = cname
        self.daylength = 0  # measured in RL hours
        self.yearlength = 0  # measured in IG Days
        self.days_of_week = []
        self.months = {}
        self.monthlist = []
        self.holidays = {}
        self.watershed_name = ''
        self.watershed_date = ''

        dlength = node.find('IGDayLengthInHours')
        if dlength != None:
            try:
                self.daylength = int(strip_whitespace(dlength.text))
            except ValueError:
                log("FATAL", "IGDayLengthInHours property must be an integer", exit_code=1)

        for month in node.findall('month'):
            month_name = required_attribute(month, 'name')
            month_days = required_attribute(month, 'days')

            try:
                self.months[month_name] = int(month_days)
                self.monthlist.append(month_name)
            except ValueError:
                log("FATAL", "days property must be an integer", exit_code=1)

            if self.months[month_name] < 1:
                log("FATAL", "days must be greater than 0", exit_code=1)

        for day in node.findall('day'):
            self.days_of_week.append(strip_whitespace(day.text))

        holidays = node.findall('holiday')
        if holidays:
            holiday_compliance = True
        for holiday in holidays:
            holiday_name = required_attribute(holiday, 'name')
            holiday_mday = required_attribute(holiday, 'month_day')
            holiday_month = required_attribute(holiday, 'month')

            if holiday_name in self.holidays:
                log("FATAL", "Duplicate holiday name found.  Holiday names must be unique.", exit_code=1)

            try:
                holiday_mday = int(holiday_mday)
            except ValueError:
                log("FATAL", "month_day property must be an integer", exit_code=1)

            if holiday_month not in self.months:
                holiday_compliance = False
            elif holiday_mday > self.months[holiday_month] or holiday_mday < 1:
                holiday_compliance = False

            if (holiday_compliance):
                self.holidays[holiday_name] = { holiday_month : holiday_mday }
            else:
                log("ERROR", "Cannot create %s holiday" % holiday_name, problem=True)

        watershed = node.find('WatershedEvent')
        if watershed != None:
            ws_title = required_attribute(watershed, 'title')
            ws_date = required_attribute(watershed, 'date')
            self.watershed_name = ws_title
            self.watershed_date = ws_date + " 00:00:00"

        self.yearlength = reduce(lambda x, y: x + y, self.months.values())

    def get_current_IG_DateTime(self):
        return self.get_IG_DateTime(date_time_string())

    def get_IG_DateTime(self, date_time):
        date_diff=self.get_date_diff(date_time)
        IG_days_diff= self.get_IG_days_diff(date_diff)
        IG_date = self.get_IG_date(IG_days_diff)
        IG_date["day_of_week"] = self.get_day_of_week(IG_days_diff)
        IG_date["hour"]= self.get_IG_time(date_diff["hours"],date_diff["minutes"],date_diff["seconds"])["hours"]
        IG_date["minute"]=self.get_IG_time(date_diff["hours"],date_diff["minutes"],date_diff["seconds"])["minutes"]
        return IG_date

    # returns a RL time breakdown between a given time and the watershed date
    def get_date_diff(self,given_time):
        ret={}

        c_y,c_m,c_d,c_h,c_M,c_s = self.unpackDate(given_time)
        z_y,z_m,z_d,z_h,z_M,z_s = self.unpackDate(self.watershed_date)
        given_date = datetime.datetime(int(c_y),int(c_m),int(c_d),int(c_h),int(c_M),int(c_s))
        zero_date = datetime.datetime(int(z_y),int(z_m),int(z_d),int(z_h),int(z_M),int(z_s))
        diff = given_date - zero_date

        ret["days"] = diff.days
        ret["hours"] = diff.seconds / 3600
        remainder = diff.seconds % 3600
        ret["minutes"] = int(remainder / 60)
        ret["seconds"] = remainder % 60
        return ret

    def get_IG_days_diff(self, date_diff):
        return int((date_diff["days"]*24 + date_diff["hours"]) / self.daylength)

    def get_IG_time(self, hours, mins, seconds):
        ret={}
        remainder = (hours%self.daylength) * 3600 + (mins*60) + seconds
        IGHourlength_in_seconds = self.daylength * 150  # 3600 / 24...

        ret["hours"] = int(remainder/IGHourlength_in_seconds)
        remainder%=IGHourlength_in_seconds
        ret["minutes"]= int(remainder/(IGHourlength_in_seconds/60))
        return ret

    # given a difference in days since watershed, give the day of the week
    def get_day_of_week(self, IG_days_diff):
        IG_day_of_week_index = IG_days_diff % len(self.days_of_week)
        return self.days_of_week[IG_day_of_week_index]

    # returns a dictionary of years, months, days
    def get_IG_date(self, IGdays):
        ret = {}
        ret["year"] = IGdays / self.yearlength
        IGdays_remainder = IGdays % self.yearlength

        for month in self.monthlist:
            if IGdays_remainder > self.months[month]:
                IGdays_remainder -= int(self.months[month])
            else:
                ret["month"] = month
                ret["day"] = IGdays_remainder
                break

        return ret

    # returns list in format [month, day, year, hours, mins, seconds]
    def unpackDate(self, date):
        t_date = date.replace(" ", "/")
        t_date = t_date.replace(":", "/")
        sp = t_date.split("/")
        for x in sp:
            x = int(x)
        return sp;
