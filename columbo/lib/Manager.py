"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: Manager.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-23
#
#############################################################################################
"""
import os, commands, re, logging
from PDSPaths import *
from ColumboPath import *

class Manager:
   """
   #############################################################################################
   # Represent a manager.
   #############################################################################################
   """

   def __init__(self, loggername): # loggername is a name of your choice to refer to the logger object
      self.machine = os.uname()[1].split(".")[0]
      self.logger = logging.getLogger(loggername)
      self.logger.debug("An object of class Manager has been instantiated")

   def printInfos(self):
      print "Machine = ", self.machine

   def easyTail(self, file_path, number):
      file = open (file_path, "r")
      if (number == "all"):                              # All lines in the file
         file.seek(0, 0)
         return file.readlines()
      else:
         number = int(number)
         multiplier = number//4 + 1                      # I consider 1K is enough to 4 lines
         offset = multiplier * 1024                      # Enough character to have the few last lines
         try:
            file.seek(-offset, 2)                        # Go to the end of the file and go back "offset" characters
         except IOError:
            file.seek(0, 0)                              # If not enough bytes, we go to the beginning of the file
      return file.readlines()[-number:]                  # Array containing the last lines

