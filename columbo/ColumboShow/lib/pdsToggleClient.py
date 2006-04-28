#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pdsToggleClient.py
#
# Author: Daniel Lemay
#
# Date: 2004-10-20
#
# Description: Use to toggle (STARTED, STOPPED) a PDS client.
#
#############################################################################################
import cgi
import cgitb; cgitb.enable()
import sys, os, pwd, time, re, pickle, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from PDSPath import *
from ColumboPath import *
from CompositePDSClient import CompositePDSClient
from CompositePDSInputDir import CompositePDSInputDir
from ConfigParser import ConfigParser
from Logger import Logger
from JSMaker import JSMaker
from types import *

# Read configuration file
config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
logname = config.get('CS', 'logname')             # Full name for the logfile
log_level = config.get('CS', 'log_level')         # Level of logging
cir_host = config.get('CS', 'cir_host')           # Machine from which we can restart CIR_PROG

# If not defined in configuration file, set defaults
if (not logname ):
   logname = CS + "/log/" + "CS.log"
if (not log_level):
   log_level = "DEBUG"

# Enable logging
logger = Logger(logname, log_level, "CS")
logger = logger.getLogger()

form = cgi.FieldStorage()
clientName = form["client"].value
machinesString = form["machines"].value

logger.info("Toggle client: " + clientName)

machines = machinesString.split(",")

for index in range(len(machines)):
   machines[index] = machines[index].split(".")[0]  # Get only the first part of the hostname

TOGGLE = "/apps/pds/bin/ToggleSender.columbo"

#############################################################################################
# Toggling the client on all PDS
#############################################################################################

for machine in machines:
   command =  "sudo -u pds /usr/bin/ssh " + machine + " " + TOGGLE + " " + clientName
   (status, output) = commands.getstatusoutput(command)

command = "sudo -u pds /usr/bin/ssh " + cir_host + " python2 " + CIR_PROG + " PDS"
#print command

(status, output) = commands.getstatusoutput(command)
#print output 

#############################################################################################
# Server redirection 
#############################################################################################

URL = "pdsClientInfos.py?client=" + clientName + "&listing=0\n"
print 'Location: ', URL
