#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pxQControl.py
#
# Author: Dominik Douville-Belanger (CMC Co-op student)
#
# Description: Displays the number of files in queue for each priority settings for a circuit.
#              Allow for remote removal of whole priority queues.
#
# Date: 2005-03-17
#
#############################################################################################

import cgi
import cgitb; cgitb.enable()
import sys, os, pwd, time, re, pickle, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

import template
from PDSPath import *
from ColumboPath import *
from types import *
from myTime import *
from QObject import QObject

class InvalidDirection(Exception): pass

form = cgi.FieldStorage()
circuitName = form["circuit"].value
direction = form["direction"].value
host = form["host"].value

print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Dominik Douville-Belanger">
<meta name="Description" content="Queue Display and Control">
<meta name="Keywords" content="">
<title>Q-Control</title>
<link rel="stylesheet" type="text/css" href="/css/style.css">
<style>
</style>
<script type="text/javascript">
</script>
</head>

<body text="#000000" bgcolor="#3b87a9" link="#00ff00" vlink="ff00ff" >

<center>
""" 

template.printMainImageCenter()

print """
<table width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
   <td valign="top" align="center" bgcolor="#cccccc">
      <br>
"""

print """    </td>
  </tr>
  <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
        <blockquote>
            <font size="6"><b><pre>Queues for: %s</pre></b></font>
        </blockquote><br>
    </td>
  </tr>
  <tr>
    <td valign="top" bgcolor="#cccccc">
""" % (circuitName) 

if direction.find('tx') != -1 or direction.find('pxSender') != -1:
    direction = 'tx'
    directory = TXQ + '/' + circuitName
elif direction.find('rx') != -1 or direction.find('pxReceiver') != -1:
    direction = 'rx'
    directory = RXQ + '/' + circuitName
else:
    raise InvalidDirection
    
q = QObject(host)
print '<form method="post" action="pxFormHandler.py">'
for p in range(1, 6):
    fullpath = directory + '/' + str(p)
    number = q.count(fullpath + '/')
    if number > 0:
        print """
        <input type="checkbox" name="queueCheck" value=%s><b>Priority %s.
        </b> %d files <a href="pxQTime.py?host=%s&circuit=%s&direction=%s&priolvl=%s">-> Details</a><br><br>
        """ % (fullpath, str(p), number, host, circuitName, direction, str(p))
    else:
        print """
        <input type="checkbox" name="queueCheck" value=%s DISABLED><b>Priority %s.
        </b> %d files<br><br>
        """ % (fullpath, str(p), number)

if host == 'frontend':
    clearname = 'clear-frontend'
else:
    clearname = 'clear-backends'

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
        <input type="submit" name=%s value="Clear Q" onClick="return confirmSubmit()">
        </form>
    </td>
  </tr>
  <!-- end body -->
</center>
</body>
</html>
""" % (clearname)
