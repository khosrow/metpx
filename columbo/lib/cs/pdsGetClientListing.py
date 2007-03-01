#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pdsGetClientListing.py
#
# Author: Daniel Lemay
#
# Date: 2004-11-05
#
# CCS = Columbo Crime Scene (Each Individual PDS is a crime scene)
# CIR = Columbo Investigation Room (Investigation Room is on a LVS, clues are merged in results)
# CS  = Columbo Show (The Show is on a LVS)
#
# Description: This program lauch a program present on the CIR host that will be responsible 
# to obtain the individual listing (coming from the home directory /apps/pds/home/clientName on
# a PDS) of a PDS client. The program on the CIR host will merge the results and send them to
# the CS host. A redirection to pdsClientInfos.py with listing=1 will ensure that the listing
# is presented in HTML format.
#############################################################################################
import cgi
import cgitb; cgitb.enable()
import sys, os, pwd, time, re, pickle, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from PDSPath import *
from ColumboPaths import *
from CompositePDSClient import CompositePDSClient
from CompositePDSInputDir import CompositePDSInputDir
from ConfigParser import ConfigParser
from Logger import Logger
from JSMaker import JSMaker
from types import *
from myTime import *

# Read configuration file
config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
logname = config.get('CS', 'logname')             # Full name for the logfile
log_level = config.get('CS', 'log_level')         # Level of logging

# If not defined in configuration file, set defaults
if (not logname ):
   logname = CS + "/log/" + "CS.log"
if (not log_level):
   log_level = "DEBUG"

# Enable logging
logger = Logger(logname, log_level, "CS")
logger = logger.getLogger()

form = cgi.FieldStorage()
clientName = form["clientName"].value
host = form["host"].value
machinesString = form["machinesString"].value

logger.info("Execution pdsGetClientListing.py for: " + clientName)

if (form.has_key("glob")):
   glob = form["glob"].value
else:
   glob = ".*"

if (form.has_key("endDate")):
   endDate = form["endDate"].value
   epochEndDate = int(convertToEpoch(endDate))
else:
   epochEndDate = int(now())
   endDate = epochFormatted(epochEndDate)

if (form.has_key("startDate")):
   startDate = form["startDate"].value
   epochStartDate = int(convertToEpoch(startDate))
else:
   epochStartDate = int (epochEndDate - 4 * HOUR)
   startDate = epochFormatted(epochStartDate)

if (form.has_key("maxFiles")):
   maxFiles = form["maxFiles"].value
else:
   maxFiles = '10000'

#############################################################################################
# Lauching the program on CIR station to get a listing for the client 
#############################################################################################
command = "sudo -u pds /usr/bin/ssh " + host + " python2 " + LISTING_PROG_STARTER + ' "%s" "\'%s\'" %s %s %s' % (clientName, glob, epochStartDate, epochEndDate, maxFiles)

(status, output) = commands.getstatusoutput(command)

#############################################################################################
# Server redirection 
#############################################################################################

if (glob == '.*'):
   glob = ""

URL = "pdsClientInfos.py?client=" + clientName + "&listing=1" + "&glob=" + glob + "&startDate=" + startDate + "&endDate=" + endDate + "&maxFiles=" + maxFiles + "\n"
print 'Location: ', URL

"""
print "Content-Type: text/html"
print

print  "clientName = %s" % (clientName) 
print  "machinesString = %s" % (machinesString) 
print  "glob = %s" % (glob) 
print  "startDate = %s" % (startDate) 
print  "endDate = %s" % (endDate) 
print  "maxFiles = %s" % (maxFiles)
print command
print output
"""
