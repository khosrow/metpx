"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: myTime.py
#
# Author: Daniel Lemay
#
# Date: 2004-11-05
#
# Description: Utils time functions
#
#############################################################################################

import time, re

now = time.time

MIN = 60            #Number of seconds in a minute
HOUR = 60 * MIN     #Number of seconds in an hour
DAY = 24 * HOUR     #Number of seconds in a day

def epochFormatted (epochTime):
   return time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(epochTime))

def convertToEpoch (usFormatTime):
   regex = re.compile(r'^(?P<day>\d+)-(?P<month>\d+)-(?P<year>\d+) (?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)$')
   match = regex.search(usFormatTime)
   time_struct = (int(match.group('year')), int(match.group('month')), int(match.group('day')), int(match.group('hours')), int(match.group('minutes')), int(match.group('seconds')), 0, 1, 0)
   return time.mktime(time_struct)
