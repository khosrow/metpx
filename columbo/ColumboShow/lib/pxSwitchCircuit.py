#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: switchCircuit.py
#
# Author: Dominik Douville-Belanger (CMC Co-op student)
#
# Description: Switches on or off a circuit
#
# Date: 2005-06-29
#
#############################################################################################

import cgi
import cgitb; cgitb.enable()
import sys, os, pwd, time, re, pickle, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from PDSPath import *
from ColumboPath import *
from types import *
from myTime import *
from ConfigParser import ConfigParser

config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
action_logname = config.get('LOG', 'action_log') # Will be usefull eventually to log the action done
backends = config.get('CIR', 'backends').split(' ')
frontend = config.get('CIR', 'frontend').split(' ')

def returnToPage(circuitName, side):
    print """
        <script LANGUAGE="JavaScript">
            location.href = "circuitInfos.py?circuit=%s&backend=%s"
        </script>
    """ % (circuitName, side)

####################################################
# type must either be pxSender or pxReceiver
####################################################
form = cgi.FieldStorage()
mode = form["mode"].value
name = form["name"].value
type = form["type"].value
machine = form["machine"].value

if machine == "frontend":
    hosts = frontend
else:
    hosts = backends

print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Dominik Douville-Belanger">
<meta name="Description" content="Switches a circuit's state">
<meta name="Keywords" content="">
<link rel="stylesheet" type="text/css" href="/css/style.css">
<style>
</style>
<script type="text/javascript">
</script>
</head>
""" 

if mode == 'on':
    #command = '"/apps/px/bin/%s %s start"' % (type, name)
    action = 'start'
    
elif mode == 'off':
    #command = '"/apps/px/bin/%s %s stop"' % (type, name)
    action = 'stop'
   
for host in hosts:
    #os.system('sudo -u pds /usr/bin/ssh %s %s' % (backend, command))
    status, output = commands.getstatusoutput('sudo -u pds /usr/bin/ssh %s pxTogglerFromColumbo %s %s %s &' % (host, type, name, action))
    print status
    print output

# Recalculate the results
status, output = commands.getstatusoutput("%s %s" % (CIR_PROGRAM, 'PX'))
returnToPage(name, machine)

print """
</html>
"""
