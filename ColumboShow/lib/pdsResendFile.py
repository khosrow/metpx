#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pdsResendFile.py
#
# Author: Daniel Lemay
#
# Date: 2004-11-12
#
# Description: Used to resend a file to a PDS client
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
filename = form["filename"].value

RESEND = "/apps/pds/bin/pdsresend"

def extractMachine (filename):
   regex = re.compile(r'(.*?:){7,7}(.*?):')
   match = regex.match(filename)
   if (match):
      return match.group(2)
   else:
      print "No match!"

#############################################################################################
# Resending the file
#############################################################################################
machine = extractMachine(filename)
command = "sudo -u pds /usr/bin/ssh " + machine + " " + RESEND + " " + filename + " " + clientName
(status, output) = commands.getstatusoutput(command)

# Verification in the log file that the resend operation has been a success
date = time.strftime("%Y%m%d", time.gmtime())
resendLog = "/apps/pds/log/pdsresend.%s.%s" % (clientName, date)
command = "sudo -u pds /usr/bin/ssh " + machine + " " + "tail -n 1" + " " + resendLog
(status, output) = commands.getstatusoutput(command)
logger.info(output)
#############################################################################################
# HTML creation
#############################################################################################
print "Content-Type: text/html"
print

print "<html>"
print """
<head>
<script type="text/javascript">
function back() {
   history.go(-1)
}
function backHome (){
   alert("%s")
   back()
   //setTimeout('back()', 5000)
}
</script>
</head>
""" % (output)

print """
<body>
<script type="text/javascript">
   backHome()
</script>
</body>
</html>
"""
