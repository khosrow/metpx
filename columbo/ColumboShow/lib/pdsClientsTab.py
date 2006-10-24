#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pdsClientsTab.py
#
# Author: Daniel Lemay
#
# Date: 2004-10-08
#
# CCS = Columbo Crime Scene (Each Individual PDS is a crime scene)
# CIR = Columbo Investigation Room (Investigation Room is on a LVS, clues are merged in results)
# CS  = Columbo Show (The Show is on a LVS)
#
# Description: Main file for the Columbo Show. This program is executed when someone connects to
# the web address: columbo. The two main tasks are:
#
# 1) Read the "results" file sent by CIR host.
# 2) Present the "results" in HTML format.
#############################################################################################
import cgi
import cgitb; cgitb.enable()
import sys, os, pwd, time, re, pickle, commands, fcntl
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from PDSPath import *
from ColumboPath import *
from CompositePDSClient import CompositePDSClient
from CompositePDSInputDir import CompositePDSInputDir
from ConfigParser import ConfigParser
from JSMaker import JSMaker
from Logger import Logger
import template

def unarchiveResults(filename):
   compteur = 0
   while True:
      if compteur == 10:
         break
      try:
         file = open(filename, "rb")
         #fcntl.flock(file, fcntl.LOCK_SH)
         compositeClientDict = pickle.load(file)
         compositeInputDirDict = pickle.load(file)
         #fcntl.flock(file, fcntl.LOCK_UN)
         file.close()
         break
      except:
         (type, value, tb) = sys.exc_info()
         #print("type: %s, value: %s" % (type, value))
         compteur += 1
         #fcntl.flock(file, fcntl.LOCK_UN)
         file.close()
         time.sleep(1)
      else:
         #fcntl.flock(file, fcntl.LOCK_UN)
         file.close()

   return compositeClientDict, compositeInputDirDict

# Read configuration file
config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
pdsTab = config.get('PDS', 'tab')

# Server redirection if pdsTab is not ON 
if pdsTab != 'ON':
    URL = "pxCircuitsTab.py\n"
    print 'Location: ', URL

results_name = config.get('CIR', 'results_name')   # How the "results" file (sent by CIR host) will be named (path not included)
logname = config.get('CS', 'logname')              # Full name for the logfile
log_level = config.get('CS', 'log_level')          # Level of logging
timeout = int(config.get('CS', 'results_timeout')) # Number of minutes after which the "results" are considered outdated

# If not defined in configuration file, set defaults
if (not logname ):
   logname = CS + "/log/" + "CS.log"
if (not log_level):
   log_level = "DEBUG"

# Enable logging
logger = Logger(logname, log_level, "CS")
logger = logger.getLogger()
logger.debug("Execution of ColumboShow program")

#############################################################################################
# 1) Read the "results" file sent by CIR host.
#############################################################################################
clientDict, inputDirDict = unarchiveResults(INPUT_RESULTS + "/" + results_name)

#############################################################################################
# 2) Present the "results" in HTML format.
#############################################################################################
js = JSMaker()
js.createMaxers(clientDict, inputDirDict)

print "Content-Type: text/html"
print
 
def printHeader():
   print """<html>
<head>
<meta name="Author" content="Daniel Lemay">
<meta name="Description" content="Main Page for Columbo">
<!--<meta http-equiv=refresh content = 65>-->
<meta name="Keywords" content="">
<title>Columbo Show</title>
<link rel="stylesheet" type="text/css" href="/css/style.css">
<style>
</style>
<script type="text/javascript">
// Put data in a javascript array 
"""
   js.createJSArrayClients(clientDict)

   print """
</script>
<script src="/js/windowUtils.js"></script>
<script src="/js/ledTimer.js"></script>
<script src="/js/SortableTable.js"></script>
<!--<script src="/js/clock.js"></script>-->
<!--<script src="/js/liveclock.js"></script>-->
</head>
"""

printHeader()

# Unused, sorting is done via javascript
keys = clientDict.keys()
keys.sort(lambda x,y: cmp(y,x))

numberOfClients = len(keys)

headers = ["""<a href="#" title="Sort by Name" onclick="clientsTable.sort(0); drawTable(clients, 'infos_body'); return false;">Client Name</a>""",
           """<a href="#" title="Sort by Quantity" onclick="clientsTable.sort(1); drawTable(clients, 'infos_body'); return false;"> Queue </a>""",
           """<a href="#" title="Sort by timestamp" onclick="clientsTable.sort(2); drawTable(clients, 'infos_body'); return false;" >Last Log Line  </a>""" ]

print """
<body onLoad="getTime()" text="#000000" bgcolor="#3b87a9" link="#00ff00" vlink="ff00ff" >
<!--<span id="digitalclock" class="clock"></span>-->
<script type="text/javascript">
<!--show();-->
</script>

<center>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td>
      <table width="70%" bgcolor="#FFFFFF" border="0" cellpadding="0" cellspacing="0">
         <tr>
"""

template.tabsLine('pdsClients')
template.printMainImage()

print """
         </tr>
      </table>			
    </td>
  </tr>

  <tr>
    <td bgcolor="#cccccc">
      <table color="#cccccc" border="0" cellspacing="0" cellpadding="0">
        <tr>
           <td width="500" height="30" align="right" valign="bottom" bgcolor="#cccccc">
             <a href="#" title="Toggle Timer" onclick="toggleState(); return false;"><img border=0 height=21 src="/images/bluec0.gif" width=16 name=dizaines></a>
             <a href="#" title="Toggle Timer" onclick="toggleState(); return false;"><img border=0 height=21 src="/images/bluec0.gif" width=16 name=unites></a>
          </td>
          <td width="20">
          </td>
          <td align="center" valign="top" align="center" bgcolor="#cccccc">
            <br>
            <!--
            <script type="text/javascript"> 
              new LiveClock('arial', '2', '#000000', '#ffffff', 'UTC Time: ', '', '300', '0', '', '', '', 0);
              LC_InitializeClocks();
            </script>
            -->
          </td>

        </tr>
      </table>
    </td>
  </tr>
  
  <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
      <table width="90%" border="0" cellspacing="6" cellpadding="6" align="center">
        <tr>
          <td width="5%"><input type="button" value="Sort by PRIORITIES" 
           onClick='clientsTable.sort(3);drawTable(clients, "infos_body");'>
          </td>
"""
if "metser-tx" in keys:
   print """
          <td width="5%"><input type="button" value="Quick metser-tx"
           onClick="parent.location='pdsClientInfos.py?client=metser-tx&listing=0'">
          </td>
   """
print """
          <td width="5%" align="left" bgcolor="#cccccc">
           <input type="button" name="reload" value="RELOAD" onClick="location='forceReload.py?system=PDS'">
          </td>

"""
print """
          <td width="20%%" valign="middle"><b><h1>PDS Clients (%s)</h1></b></td>
""" % (numberOfClients)

print """
        </tr>
      </table>
     </td>
  </tr>

  <tr>
    <td valign="top" bgcolor="cccccc">
      <center>
"""

lastResultsInSeconds = os.stat(INPUT_RESULTS + "/" + results_name)[8]
lastResultsDate = time.strftime("%a %b %d %H:%M:%S %Y", time.gmtime(lastResultsInSeconds))
now = time.time()

if now - (timeout * 60) > lastResultsInSeconds:
   print "Last results: <b><blink><font color=RED size=18>%s %s</font></blink></b>" % (lastResultsDate, '(outdated)')
else:
   print "Last results: <font size=3>%s</font>" % (lastResultsDate)

js.staticHtmlForTable("infos", "infos_body", headers)

print """
      </center>
      <br>
      <br>
<script type="text/javascript">
var colTypes = ["ALPHABETIC", "NUMERIC", "ALPHABETIC", "PRIORITY"];
var orderStatus = [0, 0, 0, "DUMMY"];
var clientsTable = new SortableTable(colTypes, orderStatus, clients);
clientsTable.sort(3);
drawTable(clients, "infos_body");
</script>
    </td> 
  </tr>  
  <!-- end body -->

  <tr>
    <td bgcolor="#ffffff">
      <br>
      <center>
      <small> 
      [
"""
template.linksLine()

print """
      ]
      </small>
      </center>
    </td>
  </tr>
</table>
</center>

"""

print "</body>"
print "</html>"
