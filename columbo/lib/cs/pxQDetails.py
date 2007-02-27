#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pxQDetails.py
#
# Author: Dominik Douville-Belanger (CMC Co-op student)
#
# Description: Displays the files in queue for a circuit.
#              Allow for remote removal of the files.
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
timedir = form["timedir"].value
host = form["host"].value

print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Dominik Douville-Belanger">
<meta name="Description" content="Details on queue content">
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
            <font size="6"><b><pre>Priority %s files on %s for: %s</pre></b></font>
        </blockquote><br>
    </td>
  </tr>
  <tr>
    <td valign="top" bgcolor="#cccccc">
""" % (priolvl, timedir, circuitName) 

if direction.find('tx') != -1:
    directory = TXQ + '/' + circuitName
elif direction.find('rx') != -1:
    directory = RXQ + '/' + circuitName
else:
    raise InvalidDirection

print """&nbsp;<a href="pxQTime.py?host=%s&circuit=%s&direction=%s&priolvl=%s"><img src="/images/backward.png" border="0"></a><br>""" % (host, circuitName, direction, priolvl)

q = QObject(host)
fullpath = directory + '/' + priolvl + '/' + timedir
files = q.census(fullpath + '/' )

print '<form method="post" action="pxFormHandler.py">'
for file in files:
    print """
    <input type="checkbox" name="fileCheck" value=%s>%s<br>
    """ % (fullpath + '/' + file[0] + '|' + file[1], file[0] + ' : ' + file[1])

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
        <input type="submit" name="%s" value="Clear Files" onClick="return confirmSubmit()">
        </form>
    </td>
  </tr>
  <!-- end body -->

</center>

</body>
</html>
""" % (clearname)
