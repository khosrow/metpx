#!/usr/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pxSendOnAFTN.py
#
# Author: Daniel Lemay
#
# Date: 2007-01-10
#
# Description: Use to send a message on AFTN.
#
#############################################################################################
import cgi
import cgitb; cgitb.enable()
import sys, os, pwd, time, re, pickle, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from PDSPath import *
from ColumboPaths import *
from Logger import Logger
from ConfigParser import ConfigParser

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
if form.has_key("machine"):
    machine = form["machine"].value
if form.has_key("filename"):
    filename = form["filename"].value

logger.info("Send On AFTN: " + filename + " from " + machine)

#############################################################################################
# Send the message on AFTN
#############################################################################################
destination = '/apps/px/txq/aftn/1/%s' % time.strftime("%Y%m%d%H", time.gmtime())
#destination = '/apps/px/tito/tato/1/%s' % time.strftime("%Y%m%d%H", time.gmtime())


command = "sudo -u pds ssh pds@%s mkdir -p %s" % (machine, destination)
(status, output) = commands.getstatusoutput(command)

if filename[-4:] == '.ack':
    command = "sudo -u pds ssh pds@%s mv %s %s" % (machine, '/apps/px/operator/' + filename, destination + '/' + filename[:-4])
else:
    command = "sudo -u pds ssh pds@%s mv %s %s" % (machine, '/apps/px/operator/' + filename, destination)
(status, output) = commands.getstatusoutput(command)

#############################################################################################
# Server redirection 
#############################################################################################
URL = "pxMsgOp.py\n"
print 'Location: ', URL
