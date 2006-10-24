#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""
#############################################################################################
# Name: generalMonitoringTab.py
#
# Author: Daniel Lemay
#
# Date: 2004-11-15
#
# Description:
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
host = config.get('CCS', 'host')                  # Where the program to create a client listing must be initiated

# If not defined in configuration file, set defaults
if (not logname ):
   logname = CS + "/log/" + "CS.log"
if (not log_level):
   log_level = "DEBUG"

# Enable logging
logger = Logger(logname, log_level, "CS")
logger = logger.getLogger()
logger.info("Execution of generalMonitoringTab.py page")

#############################################################################################
# HTML Presentation 
#############################################################################################

print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Daniel Lemay">
<meta name="Description" content="General Monitoring">
<meta name="Keywords" content="">
<title>General Monitoring</title>
<link rel="stylesheet" type="text/css" href="/css/style.css">
<style>
</style>
<script type="text/javascript">
// Put data concerning the PDSs in a javascript array
"""
   
print """
</script>
<script src="/js/SortableTable.js"></script>
<!--<script src="/js/liveclock.js"></script>-->
</head>
""" 

print """
<body text="#000000" bgcolor="#3b87a9" link="#00ff00" vlink="ff00ff" >

<center>
<table width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td>
      <table width="70%" bgcolor="#FFFFFF" border="0" cellpadding="0" cellspacing="0">
         <tr>
"""

template.tabsLine('generalMonitoring')
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
      <h1>Not yet implemented</h1>
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
