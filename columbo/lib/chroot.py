"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

import os, sys
from ColumboPaths import *

print os.getcwd()
os.chdir(CLUES)
print os.getcwd()
file = open('mytest.txt', "r")

lines = file.readlines()

for line in lines:
   print line.strip()

os.chroot(COLUMBO_HOME)
print os.getcwd()
