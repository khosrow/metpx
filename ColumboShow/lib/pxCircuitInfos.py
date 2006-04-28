#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: circuitInfos.py
#
# Author: Dominik Douville-Belanger (CMC Co-op student)
#
# Description: Show infos for each individual PDSs in the cluster
#              Largely based on Daniel Lemay's clientInfos.py
#
# Date: 2005-02-07
#
#############################################################################################

import cgi
import cgitb; cgitb.enable()
import sys, os, pwd, time, re, pickle, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from PDSPath import *
from ColumboPath import *
from CompositeNCSCircuit import CompositeNCSCircuit
from ConfigParser import ConfigParser
from Logger import Logger
from JSMaker import JSMaker
from types import *
from myTime import *

def unarchiveResults(filename):
   file = open(filename, "rb")
   compositeCircuit = pickle.load(file)
   file.close()
   return compositeCircuit

# Read configuration file
config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
results_name = config.get('CIR', 'px_results_name')  # How the "results" file will be named (path not included)
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

#############################################################################################
# 1) Read the "results" file sent by CIR host.
#############################################################################################
form = cgi.FieldStorage()
circuitName = form["circuit"].value
host = form["host"].value
if host == "frontend":
    results_name += "_local"
circuitDict = unarchiveResults(INPUT_RESULTS + "/" + results_name)

js = JSMaker()
js.setNCSMax(circuitDict)
circuitName = form["circuit"].value
machines = circuitDict[circuitName].getHosts()

#############################################################################################
# 2) Present (HTML) the last log on each PDS
#############################################################################################

print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Dominik Douville-Belanger">
<meta name="Description" content="NCS informations">
<meta name="Keywords" content="">
<title>NCS informations</title>
<link rel="stylesheet" type="text/css" href="/css/style.css">
<style>
</style>
<script type="text/javascript">
// Put data concerning the PDSs in a javascript array
"""

js.createJSArrayNCSInfos(circuitDict, circuitName)
   
print """
</script>
<script src="/js/SortableTable.js"></script>
<!--<script src="/js/liveclock.js"></script>-->
</head>
""" 

keys = circuitDict.keys()
keys.sort(lambda x,y: cmp(y,x))

headers = ["""<a href="#" title="Sort by Machine" onclick="circuitTable.sort(0); drawTable(circuitInfos, 'circuit_body'); return false;">Machine</a>""",
           """<a href="#" title="Sort by Quantity" onclick="circuitTable.sort(1); drawTable(circuitInfos, 'circuit_body'); return false;"> Queue </a>""",
           """<a href="#" title="Cannot sort this by socket"> Socket info </a>""",
           """<a href="#" title="Log" onclick="circuitTable.sort(2); drawTable(circuitInfos, 'circuit_body'); return false;">Last Log Line  </a>"""] 
                 
print """
<body text="#000000" bgcolor="#3b87a9" link="#00ff00" vlink="ff00ff" >

<center>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
      <br>
"""
print """
      <h1>Circuit: %s </h1>
    </td>
  </tr>

  <tr>
    <td valign="top" bgcolor="#cccccc">
      <center>
""" % (circuitName) 

js.staticHtmlForTable("infos", "circuit_body", headers)

print """
      </center>
      
      <br>
<script type="text/javascript">
var colTypes = ["ALPHABETIC", "NUMERIC", "ALPHABETIC", "NUMERIC", "ALPHABETIC"];
var orderStatus = [0, 0, 0, 0, 0];
var circuitTable = new SortableTable(colTypes, orderStatus, circuitInfos);
circuitTable.sort(0);
drawTable(circuitInfos, 'circuit_body');
</script>
    </td> 
  </tr>
"""

circuit = circuitDict[circuitName]
type = circuit.getGlobalType().split(' ')[0] # Just pxSender or pxReceiver
#onPage = "pxSwitchCircuit.py?mode=on&name=%s&type=%s&host=%s" % (circuitName, type, host)
#offPage = "pxSwitchCircuit.py?mode=off&name=%s&type=%s&host=%s" % (circuitName, type, host)
#print """
#<tr>
#    <td valign="top" align="center" bgcolor="#cccccc">
#        <form>
#            <input type="button" name="switchon" value="Switch On" onclick="location='%s'">
#            &nbsp;&nbsp;&nbsp;
#            <input type="button" name="switchoff" value="Switch Off" onclick="location='%s'">
#        </form>
#    </td>
#</tr>
#""" % (onPage, offPage)

# Usual stuff
if type == 'pxReceiver':
    directory = 'rx'
elif type == 'pxSender':
    directory = 'tx'
else:
    raise ValueError

path = '/apps/px/etc/%s/%s.conf' % (directory, circuitName)
status, output = commands.getstatusoutput('sudo -u pds /usr/bin/ssh %s cat %s' % (machines[0], path))
if not status:
    result = output
else:
    result = ''
print """
<tr>
    <td valign="top" bgcolor="#cccccc">
        <h3>Config file:</h3>
        %s
    </td>
</tr>
""" % ('<br>'.join(result.splitlines()))

print """
  <!-- end body -->
</center>
"""
print "</body>"
print "</html>"
