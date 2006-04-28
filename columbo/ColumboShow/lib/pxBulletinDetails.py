#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pxBulletinDetails.py
#
# Author: Dominik Douville-Belanger (CMC Co-op student)
#
# Description: Displays a PX bulletin's contents.
#
# Date: 2005-06-20
#
#############################################################################################

import cgi
import cgitb; cgitb.enable()
import sys, pwd, time, re, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

import template
from PDSPath import *
from ColumboPath import *
from types import *
from myTime import *

import SearchUtils

form = cgi.FieldStorage()
header = form["header"].value
logpath = form["logpath"].value
host = form["host"].value
if form.has_key("dbath"):
    dbpath = form["dbpath"].value
else:
    dbpath = ''

print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Dominik Douville-Belanger">
<meta name="Description" content="Bulletin contents">
<meta name="Keywords" content="">
<title>Bulletin Details</title>
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
    </td>
  </tr>
"""

if dbpath == '':
    dbpath = SearchUtils.accessDB(header)

content = SearchUtils.readFromDB(host, dbpath)
if content != '':
    destinations = SearchUtils.possibleDestination(header, host)
    if destinations == []:
        disabled = 'DISABLED'
    else:
        disabled = ''
    print """
    <tr>
        <td valign="top" align="center" bgcolor="#cccccc">
            <blockquote>
                <font size="5"><b><pre>Bulletin content of:<br>%s</pre></b></font>
            </blockquote><br>
        </td>
    </tr>
    <tr>
    <td valign="top" bgcolor="#cccccc">
        <form method="POST" action="pxResendBulletin.py">
            &nbsp;<input type="submit" name="submit" value="Send" %s> &nbsp; &nbsp; &nbsp;
            To: <select name="destination" %s>
    """ % (header, disabled, disabled)
    for dest in destinations:
        print '<option value="%s">%s' % (dest, dest)
    print """
        </select><input type="hidden" name="dbpath" value="%s">
        <input type="hidden" name="host" value="%s"></form>""" % (dbpath, host)
    
    # Printing the bulletin's content
    print '<blockquote>%s</blockquote>' % content
    
else:
    print """
        <tr>
            <td valign="top" align="center" bgcolor="#cccccc">
                <font color="red"><center><h3>Could not locate <u>%s</u> in the database.<br><br>Please choose another result.</h3>
                <br>
                <a href="javascript:window.close();">Close this window</a></center></font>
            </td>
        </tr>
    """ % header

print"""
    </td>
  </tr>
  <!-- end body -->

</center>

</body>
</html>
"""
