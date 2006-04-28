"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PDSParser.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-27
#
#############################################################################################
"""
import os, commands, re, pickle, time, calendar, logging
from PDSPath import *
from ColumboPath import *
from PDSClient import PDSClient
from PDSInputDir import PDSInputDir
from Manager import Manager

class PDSParser:
   """
   #############################################################################################
   # Parse different PDS files
   #############################################################################################
   """

   def __init__(self):
      pass

   def getTimeArray(self, lines):

      format = "%b %d %H:%M:%S"
      regex = re.compile(r'^.* (... \d+ \d+:\d+:\d+):')
      times = []

      for line in lines:
         match = regex.search(line)
         if (match):
            timeFields = time.strptime(match.group(1), format)
            timeFields = list (timeFields)
            timeFields[0] += 104
            timeFields[8] = 1
            seconds = calendar.timegm(timeFields)
            times.append(seconds)

      return times  
