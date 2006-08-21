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
sys.path.append(sys.path[0] + "/../../lib")
sys.path.append("../../lib")
sys.path.append("/apps/px/lib/search")

import template
from PDSPath import *
from ColumboPath import *
from types import *
from myTime import *

import searchResendUtils

form = cgi.FieldStorage()
item = form["item"].value

def readFromDB(file, host):
    """
    Reads a bulletin file from the database.
    The output is copied to a temporary file on the local machine.
    Arguments:
        host   -> machine that hosts the bulletin file
        dbPath -> path to the bulletin in the database
    Returns: path to the bulletin's copy
    """
    
    dbPath = searchResendUtils.headerToLocation(file)
    command = "sudo -u pds /usr/bin/ssh %s cat %s" % (host, dbPath)
    status, output = commands.getstatusoutput(command)
    if not status:
        return output.replace('\n', '<br>')
    else:
        return ''

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
<table width="100%" bgcolor="#cccccc" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
      <br>
    </td>
  </tr>
"""

itemParts = item.split(":")
host = itemParts[0]
file = ":".join(itemParts[2:])
content = readFromDB(file, host)

if content == "":
    print """
    <tr>
        <td>
            <h3>Could not locate <u>%s</u> in the database.</h3>
        </td>
    </tr>
    """ % (file)
else:
    print """
    <tr>
        <td valign="top" align="center" bgcolor="#cccccc">
            <blockquote>
                <font size="5"><b><pre>Bulletin content of:<br>%s</pre></b></font>
            </blockquote><br>
        </td>
    </tr>
    <tr>
        <td>
            <blockquote>%s</blockquote>
        </td>
    </tr>
    """ % (file, content)
    
print"""
    </td>
  </tr>
  <!-- end body -->

</center>

</body>
</html>
"""
