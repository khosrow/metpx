"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PDSClient.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-01
#
#############################################################################################

"""
import PDSPaths
import logging

class PDSClient: 

   """
   #############################################################################################
   # Represent a PDS client.
   #############################################################################################
   """

   def __init__(self, machine, name, pid, status, date, config, logfile): 
      """
      #############################################################################################
      # Constructor of a PDSCLient object
      #############################################################################################
      """
      self.machine = machine
      self.name = name          
      self.pid = pid
      self.status = status
      self.date = date
      self.config = config 
      self.logfile = logfile
      self.queue = 0
      self.logline = []

   def setQueue(self, number):
      self.queue = number

   def getQueue(self):
      return self.queue

   def setLastLog(self, logline):
      self.logline.extend(logline)

   def getLastLog(self):
      return self.logline
 
   #def __repr__(self):
   
#   return "[CLIENT OBJECT: %s %20s %6s %8s %18s %6d ]" % (self.machine, self.name, self.pid, self.status, self.date, self.queue)

   def __repr__(self):
      return "[%s %8s %6d %s]" % (self.machine, self.status, self.queue, self.logline)
