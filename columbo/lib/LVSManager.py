"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: LVSManager.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-23
#
#############################################################################################
"""
import os, commands, re, logging
from PDSPaths import *
from ColumboPaths import *
from Manager import Manager

class LVSManager(Manager):
   """
   #############################################################################################
   # Represent a LVS manager.
   #############################################################################################
   """

   def __init__(self, loggername): # loggername is a name of your choice to refer to the logger object
      Manager.__init__(self, loggername)  
      self.logger.debug("An object of class LVSManager has been instantiated")
 
   def getMachines(self, ipvsadm_regex):
      addMachines = False
      command = 'sudo -u root /sbin/ipvsadm'
      (status, output) = commands.getstatusoutput(command)
      lines = output.splitlines()
      regex1 = re.compile(r'TCP  %s.*:ftp rr' % ipvsadm_regex)
      regex2 = re.compile(r'-> (\S+):ftp')
      machines = []
      for line in lines:
         match1 =  regex1.search(line)
         if (match1):
            #print line
            addMachines = True
            continue
         if addMachines:
            match2 =  regex2.search(line)
            if match2:
               machines.append(match2.group(1))
            else:
               addMachines = False

      self.logger.debug("Machines List obtained from LVSManager: " + str(machines))
      return machines

