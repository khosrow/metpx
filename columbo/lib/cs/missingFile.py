#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: missingFile.py
#
# Author: Daniel Lemay
#
# Description: Display this page when a file is missing
#
# Date: 2006-09-27 
#
#############################################################################################

import cgi
import cgitb; cgitb.enable()
import sys, os, pwd, time, re, pickle, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from PDSPath import *
from ColumboPath import *
import template

form = cgi.FieldStorage()
filename = form["filename"].value
image = int(form["image"].value)

keys = os.environ.keys()
keys.sort()

print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Daniel Lemay">
<meta name="Description" content="Error Message">
<meta name="Keywords" content="">
<title>Missing File</title>
<link rel="stylesheet" type="text/css" href="/css/style.css">
<style>
</style>
<script type="text/javascript">
</script>
</head>
<body text="#000000" bgcolor="#3b87a9" link="#00ff00" vlink="ff00ff" >
<center>
"""

if image:
    template.printMainImageCenter()

#print "<br>"
#for key in keys:
#    print "%s = %s <br>" % (key, os.environ[key])

print """
<table width="100%%" border="0" cellpadding="0" cellspacing="0">
  <tr>
   <td valign="top" align="center" bgcolor="#cccccc">
      <br>
  </td>
  </tr>
  <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
        <blockquote>
            <font size="6"><b><pre>Missing File (%s)</pre></b></font>
            <font size="7" color="red"><b><pre>Contact DADS Pager</pre></b></font>
        </blockquote>
    </td>
  </tr>
</table>
</center>
</body>
</html>
""" % (filename)
