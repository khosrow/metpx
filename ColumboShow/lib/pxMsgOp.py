#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pxMsgOp.py
#
# Author: Dominik Douville-Belanger (CMC Co-op student)
#
# Description: Displays special bulletin files containing messages for the operators.
#
# Date: 2005-04-04
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
from Logger import Logger
import template

import MsgOpUtils

config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
action_logname = config.get('LOG', 'action_log')

logger = Logger(action_logname, "INFO", "AL")
logger = logger.getLogger()

print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Dominik Douville-Belanger">
<meta name="Description" content="Message center for the operators">
<meta name="Keywords" content="">
<META HTTP-EQUIV="Pragma" CONTENT="no-cache">
<META HTTP-EQUIV="Expires" CONTENT="-1">
<title>Operator Messages</title>
<link rel="stylesheet" type="text/css" href="/css/style.css">
<style>
</style>
<script type="text/javascript">
</script>
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
"""

# The form handler is embeded inside the web page
# since it is quite short and straight-forward
form = cgi.FieldStorage()
if form.has_key('delCheck'):
    msgDel = form.getlist('delCheck')
    for md in msgDel:
        md = md.split('|')
        header = md[0]
        machine = md[1]
        status, result = MsgOpUtils.removeMsg(header, machine)
        if status == 0:
            logger.info('Operator Messages: %s was deleted' % (header))
        else:
            logger.error('Operator Messages: %s could not be deleted' % (header))

print """    </td>
  </tr>
  <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
        <blockquote>
            <font size="6"><b><pre>Available messages:</pre></b></font>
        </blockquote><br>
    </td>
  </tr>
  <tr>
    <td valign="top" bgcolor="#cccccc">
"""
msgs = MsgOpUtils.getMsg()

# We want the new messages to be displayed first
acknowledged = []
new = []
for msg in msgs:
    if msg[0].find('.ack') != -1:
        acknowledged.append(msg)
    else:
        new.append(msg)
acknowledged.sort()
new.sort()
msgs = new + acknowledged

print '<form method="post" action="pxMsgOp.py">'
for msg in msgs:
    displayHeader = header = msg[0]
    machine = msg[1]
    if header.find('.ack') != -1:
        displayHeader = header[:-4]
        print """
        <input type="checkbox" name="delCheck" value=%s>
        <a href="pxMsgDetails.py?msg=%s&machine=%s">%s</a><br><br>
        """ % (header + '|' + machine, header, machine, displayHeader)
    else:
        print """
        <input type="checkbox" name="delCheck" value=%s DISABLED>
        <a href="pxMsgDetails.py?msg=%s&machine=%s"><b>%s</b></a><br><br>
        """ % (header + '|' + machine, header, machine, header)

print """
      <br>
    </td>
  </tr>
  <tr>
    <script LANGUAGE="JavaScript">
        function confirmSubmit()
        {
            var answer=confirm("Are you sure?");
            if (answer)
	            return true;
            else
	            return false;
        }
    </script>
    <td valign="top" bgcolor="#cccccc">
        <input type="submit" name="delete" value="Delete" onClick="return confirmSubmit()">
        </form>
    </td>
  </tr>
  <!-- end body -->
"""
print """
<table>
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
print '<head><META HTTP-EQUIV="Pragma" CONTENT="no-cache"><META HTTP-EQUIV="Expires" CONTENT="-1"></head>'
print "</html>"
