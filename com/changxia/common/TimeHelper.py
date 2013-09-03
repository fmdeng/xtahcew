#!/usr/bin/python
#-*-coding:utf-8-*-

import time
from time import *
import time
import re
'''处理时间的一些通用函数'''
class TimeHelper:

    def getDateTimeFromSeconds(self, second, format="%Y-%m-%d %H:%M:%S"):
        '''给定seconds，返回DATE_TIME（YYYY-MM-DD HH:SS)'''
        date_time_str = strftime(format, localtime(second) )
        return date_time_str

    def getDateHourMin(self, date_time_str):
        '''给定 DATE_TIME(YYYY-MM-DD HH:MM:SS 返回日期，小时，分钟'''
        try:
            date_other = re.split("[ ]+", date_time_str)
            date = date_other[0]
            hour_min = re.split("[ :]+", date_other[1])
            return_result = (date, hour_min[0], hour_min[1])
            return return_result
        except:
            return ("-1", "-1", "-1")

    def getSecondsFromDateTime(self, date_time_str):
        '''给定 DATE_TIME(YYYY-MM-DD HH:SS) 返回seconds'''
        timelist = re.split("[\- :]+", date_time_str)
        while len(timelist) <> 9:
            timelist.append(0)
        for i in xrange(9):
            timelist[i] = int(timelist[i])
        secconds = mktime(timelist)
        return int(secconds)

    def getCurrentDate(self):
        '''获得当前时间以str格式表示'''
        return self.getDateBeforeAfter(num_date=0)

    def getDateBeforeAfter(self, num_date = 1):
        '''获得相对于今天多少天的日期'''
        day_seconds = 60 * 60 * 24
        now = localtime()
        now = mktime(now)
        date_time_str = self.getDateTimeFromSeconds(now + num_date * day_seconds)
        date_str = date_time_str.split()
        return date_str[0]

    def diffDate(self, date_one, date_two):
        '''给出两个日期相差的天数，日期的格式是YYYY-MM-DD HH:MM:SS'''
        date_one_second = self.getSecondsFromDateTime(date_one)
        date_two_second = self.getSecondsFromDateTime(date_two)
        day_seconds = 60 * 60 * 24
        return (date_two_second - date_one_second ) /day_seconds ;

    def getRangeDateStr(self, date_one, date_two, num=30):
        '''给出两个日期之间所有的时期，包括这两个日期'''
        date_one_second = self.getSecondsFromDateTime(date_one)
        date_two_second = self.getSecondsFromDateTime(date_two)
        min_date = int(date_one_second) 
        max_date = int(date_two_second)
        if min_date > int(date_two_second):
            min_date = int(date_two_second)
            max_date = int(date_one_second)
        day_seconds = 60 * 60 * 24
        result_return = []
        seconds = min_date
        while seconds <= max_date:
             date_time_str = self.getDateTimeFromSeconds(seconds)
             date_info = date_time_str.split()
             try:
                 result_return.append(date_info[0])
             except:
                 pass
             seconds = seconds + day_seconds
        return result_return[-1*num:]

    def getWeekDay(self, date_str):
        '''回答日期(YYYY-MM-DD HH:MM:SS)是星期几'''
        date_seconds = self.getSecondsFromDateTime(date_str)
        week_day = strftime("%w", localtime(date_seconds) )
        return week_day

    def currentTime(self, format="%Y-%m-%d %H:%M:%S"):
        '''获得当前时间(YYYY-MM-DD HH:MM:SS)'''
        seconds = self.currentSeconds()
        return self.getDateTimeFromSeconds(seconds)
    def currentSeconds(self):
        '''获得当前的秒'''
        return int(time.time())

if __name__=="__main__":
    org_second = 4294967295 ;
    org_second = 1375027200;
    time_helper = TimeHelper()
    print "seconds is : "  + str ( org_second)
    time_str = time_helper.getDateTimeFromSeconds(org_second )
    print time_str + "-----------------"
    org_second = 1314098711;
    time_helper = TimeHelper()
    print "seconds is : "  + str ( org_second)
    time_str = time_helper.getDateTimeFromSeconds(org_second )
    print time_str
    seconds = time_helper.getSecondsFromDateTime(time_str)
    print seconds
    print time_helper.getDateTimeFromSeconds(seconds )
    time_str="2011-10-15 00:00:00"
    print "$$$$$$$$$$$$",
    print time_helper.getSecondsFromDateTime(time_str)
    print "current date: " + time_helper.getCurrentDate()
    print "tommorrow: " + time_helper.getDateBeforeAfter(1)
    print "yesterday: " + time_helper.getDateBeforeAfter(-1)
    print "SECONDS: " + str(time_helper.getSecondsFromDateTime("2011-08-03"))
    print "DIFF DATE: " + str(time_helper.diffDate("2011-07-08", '2011-06-25'))
    print  time_helper.getDateHourMin("2011-08-03 08:45:12")
    print  time_helper.getDateHourMin("2011-08-0308:45:12")
    print  time_helper.getDateHourMin("2011-08-03 15:30:33")
    print  time_helper.getRangeDateStr("2011-08-03 00:00:00", "2011-07-29 00:00:00")
    print  time_helper.getRangeDateStr("2011-08-03 00:00:00", "2011-07-29 00:00:00", 2)
    print time_helper.getWeekDay("2011-10-23")
    print time_helper.currentSeconds()
    print time_helper.currentTime()
