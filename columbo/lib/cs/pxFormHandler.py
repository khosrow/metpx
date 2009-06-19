#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

##################################################################
# Name: pxFormHandler.py
#
# Author: Dominik Douville-Belanger
#
# Date: 2005-03-25
#
# Description: Call the file eraser in the proper mode based
#              on user checkbox choice in the Q webpages.
#
##################################################################

import cgi
import cgitb; cgitb.enable()
import commands
import re
import sys
import os

sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib");

from PDSPath import *
from ColumboPaths import *
from Logger import Logger
from ConfigParser import ConfigParser

config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
action_logname = config.get('LOG', 'action_log')
backends = config.get('CIR', 'backends').split(' ')
frontend = config.get('CIR', 'frontend').split(' ')

class InvalidPath(Exception): pass

logger = Logger(action_logname, "INFO", "AL")
logger = logger.getLogger()

def returnToPage(pageName, local, parameters):
    print '<script LANGUAGE="JavaScript">'
    if not local: # Where to return?
        print 'location.href = "%s?host=backends%s"' % (pageName, parameters)
    else:
        print 'location.href = "%s?host=frontend%s"' % (pageName, parameters)
    print '</script>'

def whichWay(str):
    if str == 'txq':
        return 'tx'
    elif str == 'rxq':
        return 'rx'

print "Content-Type: text/html"
print
print """
<html>
    <head>
    </head>
    <body>
"""

prioDel = []
timeDel = []
fileDel = []
form = cgi.FieldStorage()
if form.has_key("clear-frontend"): # Needed to distinguish between local and backend
    local = 1
    hosts = frontend
else:
    local = 0
    hosts = backends[:]

###############################################################
# To understand this code it is better to keep in mind the
# of each filename's path.
# /apps/px/txq/amis/3/20050520/<bulletins>
#    1  2   3   4   5     6         7
# When we .split('/') a string like this, the first '/' at
# the beginning gives us a "" string in the result list.
# This is why the first element of interest (apps) is at
# position 1
###############################################################

if form.has_key("queueCheck"): # Erasing entire priority queue
    prioDel = form.getlist("queueCheck")
    elements = prioDel[0].split('/')
    direction = whichWay(elements[3])
    name = elements[4]
    stringArguments = ''
    for p in prioDel:
        stringArguments += p.split('/')[5] + ' ' # Extract all priorities to delete
    for host in hosts:
        status, output = commands.getstatusoutput('sudo -u pds /usr/bin/ssh %s /apps/pds/tools/Columbo/lib/qcleaner.py --type %s --name %s %s' % (host, direction, name, stringArguments))
        if status == 0:
            logger.info("QCleaner: %s (%s) cleaning priorities: %s -> OK" % (name, host, stringArguments))
        else:
            logger.error("QCleaner: %s (%s) cleaning priorities: %s -> FAIL" % (name, host, stringArguments))
        
    parameters = '&circuit=%s&direction=%s' % (name, direction)
    returnToPage('pxQControl.py', local, parameters)
        
elif form.has_key("timeCheck"): # Erasing an hour's content
    timeDel = form.getlist("timeCheck")
    elements = timeDel[0].split('/')
    direction = whichWay(elements[3])
    name = elements[4]
    priority = elements[5]
    stringArguments = ''
    for t in timeDel:
        stringArguments += t.split('/')[6] + ' ' # Extract all hours to delete
    for host in hosts:
        status, output = commands.getstatusoutput('sudo -u pds /usr/bin/ssh %s /apps/pds/tools/Columbo/lib/qcleaner.py --type %s --name %s -p %s %s' % (host, direction, name, priority, stringArguments))
        if status == 0:
            logger.info("QCleaner: %s (%s) under priority %s cleaning hourly directories: %s -> OK" % (name, host, priority, stringArguments))
        else:
            logger.error("QCleaner: %s (%s) under priority %s cleaning hourly directories: %s -> FAIL" % (name, host, priority, stringArguments))
            
    parameters = '&circuit=%s&direction=%s&priolvl=%s' % (name, direction, priority)
    returnToPage('pxQTime.py', local, parameters)
            
elif form.has_key("fileCheck"): # Erasing file by file
    fileDel = form.getlist("fileCheck")
    elements = fileDel[0].split('/')
    direction = whichWay(elements[3])
    name = elements[4]
    priority = elements[5]
    hour = elements[6]
    stringArguments = ''
    machineCommandDict = {}
    # We sort all filename in dictionary with their host as the key (e.g. {'pds5' : 'bulletin1', 'pds6' : 'bulletinA bulletinB'})
    for f in fileDel:
        bulletinName, host = f.split('/')[7].split('|')
        if host not in machineCommandDict:
            machineCommandDict[host] = bulletinName + ' '
        else:
            machineCommandDict[host] += (bulletinName + ' ')
    for host in machineCommandDict.keys():
        stringArguments = machineCommandDict[host]
        status, output = commands.getstatusoutput('sudo -u pds /usr/bin/ssh %s /apps/pds/tools/Columbo/lib/qcleaner.py --type %s --name %s -p %s -h %s %s' % (host, direction, name, priority, hour, stringArguments))
        if status == 0:
            logger.info("QCleaner: %s (%s) under priority %s time %s cleaning files: %s -> OK" % (name, host, priority, hour, stringArguments))
        else:
            logger.error("QCleaner: %s (%s) under priority %s time %s cleaning files: %s -> FAIL" % (name, host, priority, hour, stringArguments))
            
    parameters = '&circuit=%s&direction=%s&priolvl=%s&timedir=%s' % (name, direction, priority, hour)
    returnToPage('pxQDetails.py', local, parameters)

print """
        <script language=JavaScript>
            window.close();
        </script>
    </body>
</html>
"""

print '</body></html>'
