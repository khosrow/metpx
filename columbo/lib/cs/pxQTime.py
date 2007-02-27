#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pxQTime.py
#
# Author: Dominik Douville-Belanger (CMC Co-op student)
#
# Description: Displays the number of files in queue for a specific time for a given circuit.
#              Allow for remote removal of a complete time queue directory the files.
#
# Date: 2005-03-23
#
#############################################################################################

import cgi
import cgitb; cgitb.enable()
import sys, os, pwd, time, re, pickle, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

import template
from PDSPath import *
from ColumboPaths import *
from types import *
from myTime import *
from QObject import QObject

class InvalidDirection(Exception): pass

form = cgi.FieldStorage()
circuitName = form["circuit"].value
direction = form["direction"].value
priolvl = form["priolvl"].value
host = form["host"].value

print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Dominik Douville-Belanger">
<meta name="Description" content="Queue display by priority and time">
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
            <font size="6"><b><pre>Priority %s time directories for: %s</pre></b></font>
        </blockquote><br>
    </td>
  </tr>
  <tr>
    <td valign="top" bgcolor="#cccccc">
""" % (priolvl, circuitName)

if direction.find('tx') != -1:
    directory = TXQ + '/' + circuitName
elif direction.find('rx') != -1:
    directory = RXQ + '/' + circuitName
else:
    raise InvalidDirection


print """&nbsp;<a href="pxQControl.py?host=%s&circuit=%s&direction=%s"><img src="/images/backward.png" border="0"></a><br>""" % (host, circuitName, direction)

q = QObject(host)
fullpath = directory + '/' + priolvl
timedirs = q.timedir(fullpath + '/')
print '<form method="post" action="pxFormHandler.py">'
for t in timedirs:
    number = q.count(fullpath + '/' + t + '/')
    if number > 0:
        print """
        <input type="checkbox" name="timeCheck" value=%s><b>%s:
        </b> %d files in queue <a href="pxQDetails.py?host=%s&circuit=%s&direction=%s&priolvl=%s&timedir=%s">-> Details</a><br><br>
        """ % (fullpath + '/' + t, t, number, host, circuitName, direction, priolvl, t)
    else:
        print """
        <input type="checkbox" name="timeCheck" value=%s DISABLED><b>%s:
        </b> %d files in queue<br><br>
        """ % (fullpath + '/' + t, t, number)

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
        <input type="submit" name=%s value="Clear directory" onClick="return confirmSubmit()">
        </form>
    </td>
  </tr>
  <!-- end body -->

</center>
</body>
</html>
""" % (clearname)
