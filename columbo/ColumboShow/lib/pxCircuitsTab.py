#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pxCircuitsTab.py
#
# Author: Dominik Douville-Belanger (CMC Co-op Student)
#         Largely based on Daniel Lemay's ColumboShow.py
#
# Date: 2005-02-02
#
# Description: Show time for the PX Applications and Circuits informations
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
import template

import MsgOpUtils

def checkMessages():
    """
    Verifies if there are available message for the operators.
    If there is at least one unread message, the indicator will change color to red.
    If all messages left are acknowledge, the indicator will be yellow.
    If there are no messages waiting, it will be green.
    """
    msgs = MsgOpUtils.getMsg()
    new = 0
    acknowledged = 0
    for msg in msgs:
        if msg[0].find('.ack') == -1:
            new += 1
        else:
            acknowledged += 1
    print '<table width="5%" border="0" cellpadding="2"><tr><td width="40" bgcolor="#cccccc"></td><td>'
    if new > 0:
        print '<table bgcolor="red" border="1" cellpadding="2">'
    elif acknowledged > 0:
        print '<table bgcolor="yellow" border="1" cellpadding="2">'
    else:
        print '<table bgcolor="lightgreen" border="1" cellpadding="2">'
    print '<tr><td><a href="pxMsgOp.py">Operator Messages</a></td></tr></table>'
    print '</td></tr></table>'
    
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
<script src="/js/ledTimer.js"></script>
<script src="/js/SortableTable.js"></script>
<!--<script src="/js/clock.js"></script>-->
<!--<script src="/js/liveclock.js"></script>-->
</head>
"""

printHeader()

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

template.tabsLine('pxCircuits')
template.printMainImage()

print """
         </tr>
      </table>			
    </td>
  </tr>

  <tr>
    <td bgcolor="#cccccc">
        <table color="#cccccc" border="0" cellspacing="0" cellpadding="0">
        <tr><td valign="top" bgcolor="#cccccc">"""
        
checkMessages()

print """</td>

          <td width="15%" align="left" bgcolor="#cccccc">
            <input type="button" name="search" value="Search logs" onClick="location='pxSearchQuery.py'">
          </td>
          <td align="center" bgcolor="#cccccc">
            <input type="button" name="reload" value="RELOAD" onClick="location='forceReload.py?system=PX'">
          </td>
           <td width="250" height="30" align="right" valign="center" bgcolor="#cccccc">
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
</table>
</center>

<iframe src="pxCircuitsTable.py?host=backends" name="backends" width=100% height=58%></iframe>
<br>
<iframe src="pxCircuitsTable.py?host=frontend" name="frontend" width=100% height=30%></iframe>
"""

print "</body>"
print "</html>"
