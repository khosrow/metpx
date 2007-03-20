#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
#############################################################################################
# Name: forceReload.py
#
# Author: Dominik Douville-Belanger
#
# Date: 2005-08-02
#
# Description: Forces the application to run again
#
#############################################################################################
import cgi
import cgitb; cgitb.enable()
import sys, commands

sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from ColumboPaths import *

form = cgi.FieldStorage()
system = form["system"].value

if system in ['PDS', 'PX']:
    COMMAND = 'sudo -u pds %s %s' % (CIR_PROG, system)
    status, output = commands.getstatusoutput(COMMAND)
    
#############################################################################################
# Server redirection 
#############################################################################################

if system == 'PDS':
    URL = "pdsClientsTab.py\n"

elif system == 'PX':
    URL = "pxCircuitsTab.py\n"

print 'Location: ', URL
