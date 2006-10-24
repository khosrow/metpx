"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: PDSInputDir.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-23
#
#############################################################################################

"""
import PDSPath
import logging

class PDSInputDir: 

   """
   #############################################################################################
   # Represent a PDS input directory 
   #############################################################################################
   """

   def __init__(self, machine, name): 
      """
      #############################################################################################
      # Constructor of a PDSInputDir object
      #############################################################################################
      """
      self.machine = machine
      self.name = name          
      self.queue = 0

   def setQueue(self, number):
      self.queue = number

   def getQueue(self):
      return self.queue

   def __repr__(self):
      return "[%s %20s %6d ]" % (self.machine, self.name, self.queue)
