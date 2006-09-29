#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pxCircuitsTable.py
#
# Author: Dominik Douville-Belanger (CMC Co-op Student)
#         Largely based on Daniel Lemay's ColumboShow.py
#
# Date: 2005-02-02
#
# Description: Show time for the PX Circuits informations
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
from JSMaker import JSMaker
from Logger import Logger

import MsgOpUtils

def unarchiveResults(filename):
   file = open(filename, "rb")
   compositeCircuitDict = pickle.load(file)
   file.close()
   return compositeCircuitDict

# Read configuration file
config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
results_name = config.get('CIR', 'results_name')
ncsResults_name = config.get('CIR', 'px_results_name')  # How the "results" file (sent by CIR host) will be named (path not included)
logname = config.get('CS', 'logname')                   # Full name for the logfile
log_level = config.get('CS', 'log_level')               # Level of logging
timeout = int(config.get('CS', 'results_timeout'))

frontend = config.get('CIR', 'frontend').split(' ')
backends = config.get('CIR', 'backends').split(' ')

# If not defined in configuration file, set defaults
if (not logname ):
   logname = CS + "/log/" + "CS.log"
if (not log_level):
   log_level = "DEBUG"

# Enable logging
logger = Logger(logname, log_level, "CS")
logger = logger.getLogger()
logger.debug("Execution of ColumboShow NCS Apps program")

form = cgi.FieldStorage()
host = ""
machines = ""
if form.has_key("host"):
    host = form["host"].value
    if host == "frontend":
        ncsResults_name += "_local"
        machines = ",".join(frontend)
    else:
        machines = ",".join(backends)

#############################################################################################
# 1) Read the "results" file sent by CIR host.
#############################################################################################
circuitDict = unarchiveResults(INPUT_RESULTS + "/" + ncsResults_name)

#############################################################################################
# 2) Present the "results" in HTML format.
#############################################################################################
js = JSMaker()
js.setNCSMax(circuitDict)

print "Content-Type: text/html"
print
 
def printHeader():
    print """<html>
    <head>
    <meta name="Author" content="Daniel Lemay/Dominik Douville-Belanger">
    <meta name="Description" content="PX Circuits infos">
    <!--<meta http-equiv=refresh content = 65>-->
    <meta name="Keywords" content="">
    <title>PX Circuits</title>
    <link rel="stylesheet" type="text/css" href="/css/style.css">
    <style>
    </style>
    <script type="text/javascript">
    // Put data in a javascript array 
    """
    js.createJSArrayNCSCircuits(circuitDict)

    print """
    </script>
    <script src="/js/SortableTable.js"></script>
    <script src="/js/windowUtils.js"></script>
    </head>
    """

printHeader()
# Unused, sorting is done via javascript
keys = circuitDict.keys()
keys.sort(lambda x,y: cmp(y,x))

headers = ["""<a href="#" title="Sort by Name" onclick="clientsTable.sort(0); drawTable(circuits, 'infos_ncs_main'); return false;">Circuit</a>""",
           """<a href="#" title="Sort by Type" onclick="clientsTable.sort(1); drawTable(circuits, 'infos_ncs_main'); return false;">Type</a>""",
           """<a href="#" title="Sort by reception time" onclick="clientsTable.sort(2); drawTable(circuits, 'infos_ncs_main'); return false;">Last _Reception_</a>""",
           """<a href="#" title="Sort by transmission time" onclick="clientsTable.sort(3); drawTable(circuits, 'infos_ncs_main'); return false;">Last Transmission</a>""",
           """<a href="#" title="Sort by Quantity" onclick="clientsTable.sort(4); drawTable(circuits, 'infos_ncs_main'); return false;"> Queue </a>""",
           """<a href="#" title="Sort by Socket State" onclick="clientsTable.sort(10); drawTable(circuits, 'infos_ncs_main'); return false;">Socket Established</a>""",
           """<a href="#" title="Sort by timestamp" onclick="clientsTable.sort(6); drawTable(circuits, 'infos_ncs_main'); return false;">Last Log Line</a>"""]

print """
<body text="#000000" bgcolor="#3b87a9" link="#00ff00" vlink="ff00ff">
<center>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td valign="top" align="left" bgcolor="#cccccc">
    </td></tr>
    <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
      <table width="90%" border="0" cellspacing="6" cellpadding="6" align="center">
        <tr>
          <td width="10%"><input type="button" value="Sort by PRIORITIES" 
            onClick='clientsTable.sort(13);drawTable(circuits, "infos_ncs_main");'>
          </td>
          <td width="10%">
            <input type="button" name="search" value="Search logs" onClick="location='pxSearchQuery.py?machines=""" + machines + """'"></td>"""
          
if host == "frontend":
    print '<td align="center" valign="middle"><b><h1>On %s</h1></b></td>' % ' '.join(frontend)
else:
    print '<td align="center" valign="middle"><b><h1>On %s</h1></b></td>' % ' '.join(backends)
print """
        </tr>
      </table>
     </td>
  </tr>

<tr>
    <td valign="top" bgcolor="cccccc">
    <center>
    """
# This checks if the results are outdated or not.
modTime = os.stat(INPUT_RESULTS + '/' + ncsResults_name).st_mtime
stringTime = time.strftime("%a %b %d %H:%M:%S %Y", time.gmtime(modTime))
currentTime = time.mktime(time.localtime())
if currentTime - (timeout * 60) > modTime:
    print """Last results: <b><font color=RED size=4>%s %s</font></b>""" % (stringTime, '(outdated)')
else:
    print """Last results: <font size=3>%s</font>""" % (stringTime)

print """
  </center></td></tr>
  <tr>
    <td valign="top" bgcolor="cccccc">
      <center>
"""

js.staticHtmlForTable("infos", "infos_ncs_main", headers)

print """
      </center>
      <br>
      <br>
<script type="text/javascript">
var colTypes = ["ALPHABETIC", "ALPHABETIC", "ALPHABETIC", "ALPHABETIC", "NUMERIC", "NUMERIC", "ALPHABETIC", "NUMERIC","NUMERIC", "NUMERIC", "NUMERIC", "NUMERIC", "NUMERIC", "PRIORITY2"];
var orderStatus = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "DUMMY"];
var clientsTable = new SortableTable(colTypes, orderStatus, circuits);
clientsTable.sort(13);"""
if host == "frontend":
    print 'drawTable(circuits, "infos_ncs_main", "frontend");'
else:
    print 'drawTable(circuits, "infos_ncs_main", "backends");'
print """
</script>
    </td> 
  </tr>  
  <!-- end body -->

  </table>
</center>

"""

print "</body>"
print "</html>"
