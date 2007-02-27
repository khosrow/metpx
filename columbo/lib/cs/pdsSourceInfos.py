#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pdsSourceInfos.py
#
# Author: Daniel Lemay
#
# Date: 2004-11-15
#
# CCS = Columbo Crime Scene (Each Individual PDS is a crime scene)
# CIR = Columbo Investigation Room (Investigation Room is on a LVS, clues are merged in results)
# CS  = Columbo Show (The Show is on a LVS)
#
# Description: Page that gives detailed (coming for each PDS) informations  about an input directory.
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
from types import *
from myTime import *
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
results_name = config.get('CIR', 'results_name')  # How the "results" file will be named (path not included)
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
logger.info("Execution of pdsSourceInfos.py page")

#############################################################################################
# Read the "results" file sent by CIR host.
#############################################################################################
clientDict, inputDirDict = unarchiveResults(INPUT_RESULTS + "/" + results_name)

js = JSMaker()
js.createMaxers(clientDict, inputDirDict)

form = cgi.FieldStorage()
inputDir = form["inputDir"].value
machines = inputDirDict[inputDir].getHosts()

machinesString = ','.join(machines)

#############################################################################################
# HTML Presentation 
#############################################################################################

print "Content-Type: text/html"
print
 
#print "Machines " + machinesString
print """<html>
<head>
<meta name="Author" content="Daniel Lemay">
<meta name="Description" content="Queue repartition">
<meta name="Keywords" content="">
<title>Queue repartition </title>
<link rel="stylesheet" type="text/css" href="/css/style.css">
<style>
</style>
<script type="text/javascript">
// Put data concerning the PDSs in a javascript array
"""
js.createJSArrayRepartitionInputDir(inputDirDict, inputDir)
   
print """
</script>
<script src="/js/SortableTable.js"></script>
<!--<script src="/js/liveclock.js"></script>-->
</head>
""" 

keys = inputDirDict.keys()
keys.sort(lambda x,y: cmp(y,x))

headers = ["""<a href="#" title="Sort by Machine" onclick="inputDirTable.sort(0); drawTable(inputDirInfos, 'inputDir_body'); return false;">Machine</a>""",
           """<a href="#" title="Sort by Quantity" onclick="inputDirTable.sort(1); drawTable(inputDirInfos, 'inputDir_body'); return false;"> Queue </a>"""]
                 
print """
<body text="#000000" bgcolor="#3b87a9" link="#00ff00" vlink="ff00ff" >

<center>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td>
      <table width="70%" bgcolor="#FFFFFF" border="0" cellpadding="0" cellspacing="0">
         <tr>
"""

template.tabsLine()
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
"""
print """
      <h1>Source Directory: %s </h1>
    </td>
  </tr>

  <tr>
    <td valign="top" bgcolor="#cccccc">
      <center>
""" % (inputDir) 

js.staticHtmlForTable("inputDir", "inputDir_body", headers)

print """
      </center>
      <br>
<script type="text/javascript">
var colTypes = ["ALPHABETIC", "NUMERIC"];
var orderStatus = [1, 0];
var inputDirTable = new SortableTable(colTypes, orderStatus, inputDirInfos);
inputDirTable.sort(0);
drawTable(inputDirInfos, "inputDir_body");
</script>
    </td> 
  </tr>  
  <!-- end body -->

  <!-- Begin footer menu --> 
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
  <!-- End footer menu --> 

</table>
</center>

"""
print "</body>"
print "</html>"
