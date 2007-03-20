"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: CompositePDSInputDir.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-28
#
#############################################################################################

"""
import PDSPaths
import logging

class CompositePDSInputDir: 

   """
   #############################################################################################
   # Represent a Composite PDS input directory 
   #############################################################################################
   """

   def __init__(self, name): 
      """
      #############################################################################################
      # Constructor of a CompositePDSInputDir object
      #############################################################################################
      """
      self.name = name          
      self.hostname = []
      self.queue = {} 
      self.compositeQueue = 0

   def addHost(self, hostname):
      self.hostname.append(hostname)

   def getHosts(self):
      return self.hostname

   def setQueue (self, hostname, number):
      self.queue[hostname] = number

   def getQueue (self, hostname):
      return self.queue[hostname]

   def setCompositeQueue (self):
      for key in self.queue.keys():
         self.compositeQueue += self.queue[key]

   def getCompositeQueue (self):
      return self.compositeQueue

   def __repr__(self):
      return "[%s %20s %6d ]" % (self.machine, self.name, self.queue)

   def __repr__(self):
      self.hostname.sort()
      print
      for host in self.hostname:
         print  "[INPUT DIR: %s %20s %6d]" % (host, self.name, self.queue[host])
      return "COMPOSITE QUEUE = " + str(self.compositeQueue)
