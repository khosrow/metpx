"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: DirectoryLister.py
#
# Author: Daniel Lemay
#
# Date: 2004-11-08
#
# CCS = Columbo Crime Scene (Each Individual PDS is a crime scene)
# CIR = Columbo Investigation Room (Investigation Room is on a LVS, clues are merged in results)
# CS  = Columbo Show (The Show is on a LVS)
#
# Description: Produce a listing (only one machine) of a client home directory
#
# This program is call by a CIR host (on a LVS). The program is installed an run
# on a CCS host (a PDS). The two tasks done by this program are:
#
# 1) Obtain infos (listing) concerning a running PDS
# 2) Send the infos (listing) to CIR Host
#
# Input parameters
#
# clientName: PDS client name for which we want a listing
# regex: simple regex about our search
# startDate: number of seconds since epoch
# endDate: number of second since epoch
# maxFiles: dummy
# copying: cp, rcp or scp
# user: pds
# host: CIR host where to send the listing
# logname: path + filename of the log file on the CCS host (a PDS)
# loglevel: logging level for logname
#
#############################################################################################
"""
import sys, os, commands, re, pickle, time
from PDSPath import *
from ColumboPath import *
from PDSClient import PDSClient
from PDSInputDir import PDSInputDir
from Manager import Manager
from ConfigParser import ConfigParser
from Sender import Sender
from Logger import Logger

DEBUG = 0

now = time.time

MIN = 60            #Number of seconds in a minute
HOUR = 60 * MIN     #Number of seconds in an hour
DAY = 24 * HOUR     #Number of seconds in a day

def epochFormatted (epochTime):
   return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(epochTime))

def convertToEpoch (usFormatTime):
   regex = re.compile(r'^(?P<day>\d+)-(?P<month>\d+)-(?P<year>\d+) (?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)$')  
   match = regex.search(usFormatTime)
   time_struct = (int(match.group('year')), int(match.group('month')), int(match.group('day')), int(match.group('hours')), int(match.group('minutes')), int(match.group('seconds')), 0, 1, 0) 
   return time.mktime(time_struct)

class DirectoryLister:
   """
   #############################################################################################
   # Represent a DirectoryLister.
   #############################################################################################
   """

   def __init__(self, pathname, startDate, endDate,  regex='.*', maxFiles = 1000): 
      self.pathname = pathname
      self.listing = []
      self.regex = re.compile(regex)
      self.nameTimeDict = {}
      self.maxFiles = int(maxFiles)
      self.startDate = int(startDate)
      self.endDate = int(endDate)

   def getListing(self):
      self.listing = os.listdir(self.pathname)
      self.listing.sort()
      return self.listing 

   def getNameTimeDict(self):
      self.getListing()
      for file in  self.listing:
         match = self.regex.search(file)
         if (match):
            #print match.group()
            epochTime = os.stat(self.pathname + '/' + file)[8]
            if ((epochTime >= self.startDate) and (epochTime <= self.endDate)):
               self.nameTimeDict[file] = [epochTime, epochFormatted(epochTime)]
      return self.nameTimeDict

   def archiveInfos(self, filename):
      file = open(filename, "wb")
      pickle.dump(self.nameTimeDict, file)
      file.close()

if (__name__ == '__main__'):

   localhost = os.uname()[1]

   # Input parameters
   (clientName, regex, startDate, endDate, maxFiles, copying, user, host, logname, log_level) = sys.argv[1:]

   # Enable logging
   logger = Logger(logname, log_level, "CCS")
   logger = logger.getLogger()
   logger.info("Beginning of DirectoryLister program on " + str(localhost))

   pathname = CLIENTHOME + "/" + clientName

   # Not used when called by CS host, may be useful when call manually and debugging
   if (regex == '0'):
      regex = '.*'
   if (maxFiles == '0'):
      maxFiles = '10000'
   if (startDate == '0' and endDate == '0'):
      endDate = now()
      startDate = endDate - 3 * HOUR
   if (endDate == '0'):
      endDate = now()
   
#############################################################################################
# 1) Obtain infos (listing) concerning a running PDS
#############################################################################################
   clientDir = DirectoryLister(pathname, startDate, endDate, regex, maxFiles)

   logger.info("Listing: " + clientName + ", " + startDate + ", " + endDate + ", " + regex)
   myDict = clientDir.getNameTimeDict()
 
   manager = Manager("CCS")
   archiveName = CLUES + '/' + clientName + "_listing." + manager.machine
   clientDir.archiveInfos(archiveName) 
    
#############################################################################################
# 2) Send the infos (listing) to CIR Host
#############################################################################################
   sender = Sender('CCS')
   sender.send(copying, user, host, archiveName, INPUT_CLUES)

   logger.info("Ending of DirectoryLister program on " + str(localhost))

   if DEBUG:
      for file in myDict.keys():
         print "%30s :  %d  %s " % (file, myDict[file][0], myDict[file][1])
   
      print pathname
      print clientDir.startDate, epochFormatted(clientDir.startDate) 
      print clientDir.endDate, epochFormatted(clientDir.endDate)
      print regex
      print clientDir.maxFiles
