"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: easyTail.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-24
#
#############################################################################################
"""
import sys, getopt
from Manager import Manager

def usage():
   message = """Should not be called directly, it is normally called by dtail"""
   print message

try:
   opts, args = getopt.getopt(sys.argv[1:], "an:u")
except getopt.GetoptError:
   usage()
   sys.exit(2)

manager = Manager("NULL")

if "-n" not in opts:
   number = 5         # Default number of lines to be viewed
for o, a in opts:
   if o == "-n":
      if a > 0:
         number = a
      else:
         print "Number of lines should be greater than 0!"
         sys.exit(2)
   if o == "-a": # We want to read all the file
      number = 'all' 
   
machine = args.pop()
filepath = args.pop()

lines = manager.easyTail(filepath, number)
for line in lines: print machine.upper() + ": " + line,
