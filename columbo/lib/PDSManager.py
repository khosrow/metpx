"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PDSManager.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-01
#
#############################################################################################
"""
import os, os.path, commands, re, pickle, time, logging
from PDSPaths import *
from ColumboPath import *
from PDSClient import PDSClient
from PDSInputDir import PDSInputDir
from Manager import Manager

DEBUG = 0

class PDSManager(Manager):
   """
   #############################################################################################
   # Represent a PDS manager.
   #############################################################################################
   """

   def __init__(self, loggername): # loggername is a name of your choice to refer to the logger object
      Manager.__init__(self, loggername)
      self.clientList = []
      self.dirList = []
      self.clientDict = {}
      self.inputDirDict = {}

   def setClientList(self):
      # UNFINISHED
      self.makeClientDict()

   def getClientList(self):
       return self.clientList

   def setDirList(self):
      # UNFINISHED
      self.makeInputDirDict()

   def getDirList(self):
       return self.dirList

   def makeClientDict(self): 
      startup = open(FULLSTARTUP, "r")

      lines = startup.readlines()

      for line in lines:
         if (re.compile(r"pdssender").search(line)):
            match = re.compile(r".* (\d+) (\S+) (\S+) (\d+) info/(\S+) log/(\S+) .*").search(line)
            (pid, name, status, date, config, logfile) =  match.group(1, 2, 3, 4, 5, 6)
            monthlyTimestamp = time.strftime("%Y%m")
            dailyTimestamp = time.strftime("%Y%m%d")
            config = ETC + "/" + config
            daily_logfile = LOG + "/" + logfile + "." + dailyTimestamp
            monthly_logfile = LOG + "/" + logfile + "." + monthlyTimestamp

            if os.path.isfile(daily_logfile):
               logfile = daily_logfile
            else:
               logfile = monthly_logfile

            lastlines = self.easyTail(logfile, 1)  # we want the 1 last lines of the logfile
            client = PDSClient(self.machine, name, pid, status, date, config, logfile)
            client.setQueue(len(os.listdir(TXQ + name + "/incoming")))
            if (len(lastlines) == 0):
               client.setLastLog(["EMPTY LOG"])
            else:
               client.setLastLog(lastlines)
            self.clientDict[name] = client

      startup.close()
   
   def makeInputDirDict(self):
      prodfile = open (FULLPROD, "r")
      lines = prodfile.readlines()

      for line in lines:
         match = re.compile(r"^in_dir\s+(\S+)").search(line)
         if (match):
            input_dir = match.group(1)
            dir = PDSInputDir(self.machine, input_dir)
            # We don't want to count file begining with a dot
            dir.setQueue(reduce(lambda x,y: x+y, map(lambda x: not x[0] == '.', os.listdir(ROOT + "/" + input_dir)), 0))
            #dir.setQueue(len(os.listdir(ROOT + "/" + input_dir)))
            self.inputDirDict[input_dir] = dir

      prodfile.close()

   def printInputDirDict(self):
      for key, value in self.inputDirDict.items():
         print "%20s => %60s" % (key, value)
  
   def printClientDict(self):
      for key, value  in self.clientDict.items():
         print "%20s => %60s" % (key, value)  

   def archiveInfos(self, filename):
      file = open(filename, "wb")
      pickle.dump(self.clientDict, file)
      pickle.dump(self.inputDirDict, file)
      file.close()

