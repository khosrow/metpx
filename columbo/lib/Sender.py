"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: Sender.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-21
#
#############################################################################################

"""
import os, logging, commands
from ColumboPaths import *

class Sender:

   """
   #############################################################################################
   # Use to send files on remote machine. Can also be used locally with cp.
   #############################################################################################
   """

   def __init__(self, loggername):
      self.logger = logging.getLogger(loggername)
   
   
   def send(self, type, user, machine, filename, remote_dir):
      """
      Send a file to a remote machine using rcp or scp
      Example: send('scp', 'pds', 'lvs1-op', '/apps/pds/tools/Columbo/ColumboInvestigationRoom/clues', '/apps/pds/')
      """
      target = user + "@" + machine

      if (type == 'scp' or type == 'rcp'):
         if type == 'scp':
            type = 'scp -q'
         command = type + ' ' +  filename + ' ' + target + ":" + remote_dir
      elif type == 'cp':
         command = type + ' ' +  filename + ' ' + remote_dir
      
      print command 
      (status, output) = commands.getstatusoutput(command)
      if not status:
         self.logger.info("%s of %s to %s on %s is OK" % (type, filename, remote_dir, machine) )
         #os.unlink(filename)
      else:
         self.logger.warning("%s: %s" % (type, output))
