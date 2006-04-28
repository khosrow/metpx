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

def returnToMainPage():
    print """
        <script type="text/javascript">
            location.href="pxMsgOp.py";
        </script>
    """

config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
action_logname = config.get('LOG', 'action_log')

logger = Logger(action_logname, "INFO", "AL")
logger = logger.getLogger()

form = cgi.FieldStorage()
msg = form["msg"].value
machine = form["machine"].value
opt = 0
if form.has_key("opt"):
    opt = form["opt"].value

print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Dominik Douville-Belanger">
<meta name="Description" content="Message details">
<meta name="Keywords" content="">
<title>Message in detail</title>
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

if msg.find('.ack') != -1:
    displayMsg = msg.strip('.ack')
else:
    displayMsg = msg

print """    </td>
  </tr>
  <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
        <blockquote>
            <font size="6"><b><pre>%s</pre></b></font>
        </blockquote><br>
    </td>
  </tr>
  <tr>
    <td valign="top" bgcolor="#cccccc">
""" % (displayMsg)

ackURL = "pxMsgDetails.py?msg=" + msg + "&machine=" + machine + "&opt=1"
rmURL = "pxMsgDetails.py?msg=" + msg + "&machine=" + machine + "&opt=2"
if opt == '1':
    MsgOpUtils.acknowledgeMsg(msg, machine)
    logger.info("Operator Messages: %s was acknowledged." % msg)
    returnToMainPage()
elif opt == '2':
    status, output = MsgOpUtils.removeMsg(msg, machine)
    if status == 0:
        logger.info('Operator Messages: %s was deleted' % (msg))
    else:
        logger.error('Operator Messages: %s could not be deleted' % (header))
    returnToMainPage()

print """
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
    <!-- Image from www.openclipart.org-->
    &nbsp;<a href=%s><img src="/images/checkmark.png" width="30" height="30" border="0"></a>
    &nbsp;&nbsp;
    <!-- Image from www.openclipart.org-->
    <a href=%s><img src="/images/editdelete.png" width="30" height="30" border="0" onClick="return confirmSubmit()"></a>
    <blockquote>
""" % (ackURL, rmURL)

# Here we print the message
print '<blockquote>%s</blockquote>' % (MsgOpUtils.msgToHTML(msg, machine))
print """
      <br>
    </td>
  </tr>
  <!-- end body -->

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
print "</html>"
