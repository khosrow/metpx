"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: CompositePDSClient.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-17
#
#############################################################################################

"""
import PDSPath, re

class CompositePDSClient: 

   """
   #############################################################################################
   # Represent a Composite PDS client.
   #############################################################################################
   """

   def __init__(self, name): 
      """
      #############################################################################################
      # Constructor of a CompositePDSCLient object
      #############################################################################################
      """
      self.name = name          
      self.hostname = []
      self.pid = {} 
      self.status = {}
      self.date = {}
      self.queue = {} 
      self.logline = {}
      self.compositeQueue = 0
      self.bestLogline = "Best logline"

   def addHost(self, hostname):
      self.hostname.append(hostname)

   def getHosts(self):
      return self.hostname

   def setPid (self, hostname, pid):
      self.pid[hostname] = pid

   def getPid (self, hostname):
      return self.pid[hostname]

   def setStatus (self, hostname, status):
      self.status[hostname] = status
   
   def getStatus (self, hostname):
      return self.status[hostname]

   def setDate (self, hostname, date):
      self.date[hostname] = date

   def getDate (self, hostname):
      return self.date[hostname]

   def setQueue (self, hostname, number):
      self.queue[hostname] = number

   def getQueue (self, hostname):
      return self.queue[hostname]

   def setLastLog (self, hostname, logline):
      self.logline[hostname] = logline

   def getLastLog (self, hostname):
      return self.logline[hostname]

   def setBestLog (self):
      items = self.logline.items()
      # items = [ (PDSName, ["logline"]) , ("pds1", ["INFO Feb 02 ..."]), ...]
      backitems = [ [val[1][0].lower(), val[1][0], val[0] ] for val in items]
      backitems.sort()
      """ Add PDS Name to the best (the more recent) logline """
      self.bestLogline = backitems[-1][1].rstrip("\n") + " ( " + backitems[-1][2].upper() + " )"
      """ If a logline begin with ERROR, select it has best logline """
      regex = re.compile(r'^ERROR|has been queued too long|Timeout')
      for orderedList in backitems:
         print orderedList[1]
         match =  regex.search(orderedList[1])
         if (match):
            self.bestLogline = orderedList[1].rstrip("\n") + " ( " + orderedList[2].upper() + " )"

   def getBestLog (self):
      return self.bestLogline

   def setCompositeQueue (self):
      for key in self.queue.keys():
         self.compositeQueue += self.queue[key]

   def getCompositeQueue (self):
      return self.compositeQueue

   def __repr__(self):
      self.hostname.sort()
      print 
      for host in self.hostname:
         print  "[CLIENT OBJECT: %20s %20s %6s %8s %18s %6d]" % (
         self.name, host, self.pid[host], self.status[host], self.date[host], self.queue[host])
         print host + ": ",  
         print self.logline[host]
      return "COMPOSITE QUEUE = " + str(self.compositeQueue)
