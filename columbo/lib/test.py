"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: test.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-01
#
# Description: Main file for the Columbo Project (PDS side)
#
#############################################################################################

"""
import sys
import os

#os.rename("toot", "tutu");
#print os.stat("PDSClient.py");

sys.path.append("../lib");
print sys.path

HOSTNAME = os.environ['HOSTNAME']
print "HOSTNAME = " + HOSTNAME

from PDSPath import *
from PDSManager import PDSManager
from PDSClient import PDSClient

#manager = PDSManager("toto")
#client = PDSClient("titi")

#print "Manager Name is: " + manager.name
#print "Client Name is: " + client.name 

uname = os.uname()

print uname

p = os.popen("date", "r");
date = p.read()
print date

p = os.popen("ls -al", "r");
ls = p.read()
print  ls

#############################################################################################
# Module that is loaded by default (Maybe the file you run or the interpreter)
#############################################################################################
print sys.modules["__main__"]

print "Now I import main"
import __main__
print __main__

print dir()
print dir(__main__)
L = __main__.__dict__.keys()
L.sort()
print L

#############################################################################################
# Code for naming a variable like the string contained in another variable
#############################################################################################
myvar = 'bonjour'
setattr(sys.modules['__main__'], myvar, "bonsoir")
print bonjour 
#############################################################################################
myvar = 'bonjour'
code = myvar + " = " +  "'bonne nuit'"
exec code
print bonjour

#############################################################################################
# eval for an expression, exec for a statement
#############################################################################################

