"""
#############################################################################################
# Name: SortableString.py
#
# Author: Daniel Lemay
#
# Date: 2004-02-01
#
# Description:
#
#############################################################################################

"""

import os.path

class SortableString:
   # Structure des strings:
   # testfileXXXX_PRI
  
   def __init__(self, string):
      self.data = string
      self.basename = os.path.basename(string)
      self.priority = None
      self.timestamp = None
      self._getKeys()

   def _getKeys(self):
      self.timestamp, self.priority = self.basename.split("_")

if __name__ == '__main__':

   ss = SortableString("toto99_2")
   print ss.data
   print ss.basename
   print ss.priority  
   print ss.timestamp
      
