#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pdsSourcesTab.py
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
# the web page: pdsSourcesTab.py. The two main tasks are:
#
# 1) Read the "results" file sent by CIR host.
# 2) Present the "results" in HTML format.
#
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
import template

def unarchiveResults(filename):
   file = open(filename, "rb")
   compositeClientDict = pickle.load(file)
   compositeInputDirDict = pickle.load(file)
   file.close()
   return compositeClientDict, compositeInputDirDict

# Read configuration file
config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
results_name = config.get('CIR', 'results_name')   # How the "results" file will be named (path not included)
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
logger.info("Execution of ColumboShowInputDirs program")

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
<meta name="Description" content="PDS Sources">
<meta http-equiv=refresh content = 65>
<meta name="Keywords" content="">
<title>Columbo Show PDS Sources</title>
<link rel="stylesheet" type="text/css" href="/css/style.css">
<style>
</style>
<script type="text/javascript">
// Put data in a javascript array 
"""
   js.createJSArrayInputDirs(inputDirDict)

   print """
</script>
<script src="/js/SortableTable.js"></script>
<!--<script src="/js/clock.js"></script>-->
<!--<script src="/js/liveclock.js"></script>-->
</head>
"""

printHeader()

# Unused, sorting is done via javascript
keys = inputDirDict.keys()
keys.sort(lambda x,y: cmp(y,x))

headers = ["""<a href="#" title="Sort by Name" onclick="inputDirsTable.sort(0); drawTable(inputDirs, 'inputDirs_body'); return false;">Input Directory</a>""",
           """<a href="#" title="Sort by Quantity" onclick="inputDirsTable.sort(1); drawTable(inputDirs, 'inputDirs_body'); return false;"> Queue </a>"""]

print """
<body text="#000000" bgcolor="#3b87a9" link="#00ff00" vlink="ff00ff" >
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

template.tabsLine('pdsSources')
template.printMainImage()

print """
         </tr>
      </table>			
    </td>
  </tr>

  <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
      <br>
      <!--
      <script type="text/javascript"> 
      new LiveClock('arial', '2', '#000000', '#ffffff', 'UTC Time: ', '', '300', '0', '', '', '', 0);
      LC_InitializeClocks();
      </script>
      -->
    </td>
  </tr>
  
  <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
      <table width="90%" border="0" cellspacing="6" cellpadding="6" align="center">
        <tr>
          <td width="10%"><input type="button" value="Sort by PRIORITIES" onClick='inputDirsTable.sort(2);drawTable(inputDirs, "inputDirs_body");'>
          </td>
          <td align="center" valign="middle"><b><h1>PDS Sources</h1></b></td>
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
   print "Last results: <b><font color=RED size=4>%s %s</font></b>" % (lastResultsDate, '(outdated)')
else:
   print "Last results: <font size=3>%s</font>" % (lastResultsDate)

js.staticHtmlForTable("inputDirs", "inputDirs_body", headers)

print """
      </center>
      <br>
      <br>
<script type="text/javascript">
var colTypes = ["ALPHABETIC", "NUMERIC", "PRIORITY1"];
var orderStatus = [0, 0, "DUMMY"];
var inputDirsTable = new SortableTable(colTypes, orderStatus, inputDirs);
inputDirsTable.sort(2);
drawTable(inputDirs, "inputDirs_body");
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
