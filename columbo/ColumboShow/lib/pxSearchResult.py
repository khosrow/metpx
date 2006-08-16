#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pxSearchResult.py
#
# Author: Dominik Douville-Belanger
#
# Description: Uses info from the search form to call the search program and shows 
#              the results.
#
# Date: 2006-08-15 (new updated version)
#
# TODO: Make the command path independent (the executable must be in the PATH)
# TODO: Make up a way to deal with errors
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

import SearchUtils
import HeaderInfo

form = cgi.FieldStorage()

def createHeaderTable(headerList):
    print '<h2><center><b>%s bulletins were found.</b></center></h2>' % len(headerList)
    print '<table width="80%" border="2" align="center">'
    print '<tr><td valign="top" align="center" bgcolor="#cccccc"><b>Header File</b></td><td valign="top" align="center" bgcolor="#cccccc"><b>Host</b></td></tr>'
    for header in headerList:
        print '<tr><td valign="top" align="center" bgcolor="#cccccc"><a href="pxBulletinDetails.py?header=%s&logpath=%s&host=%s" target="_blank">%s</a></td><td valign="top" align="center" bgcolor="#cccccc">%s</td></tr>' % (header.getHeader(), header.getLogpath(), header.getMachine(), header.getHeader(), header.getMachine())
    print '</table>'
    
print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Dominik Douville-Belanger">
<meta name="Description" content="Search for bulletins">
<meta name="Keywords" content="">
<title>Search results</title>
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

print """</td>
  </tr>
  <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
        <blockquote>
            <font size="6"><b><pre>Search results:</pre></b></font>
        </blockquote><br>
    </td>
  </tr>
  <tr>
    <td valign="top" bgcolor="#cccccc">
"""

command = "/apps/px/lib/search/pxSearch.py " # TEMPORARY

type = form["type"].value
if type == "tx":
    command += "--tx "
    startFlows = [sender.value for sender in form["senders"]]
elif type == "rx":
    command += "--rx "
    startFlows = [receiver.value for receiver in form["receivers"]]
else:
    pass # ERROR

filter = form["filter"].value
if filter == "since":
    if form.has_key("sinceinput"):
        command += "-i %s " % (form["sinceinput"].value)
    else:
        pass # ERROR
elif filter == "boundaries":
    if form.has_key("frominput") and form.has_key("toinput"):
        command += "-f %s -o %s " % (form["frominput"].value, form["toinput"].value)
    else:
        pass # ERROR

print command
sys.exit(0)

#if searchtype == 'rx':
#    logname = 'rx_' + rxselect.split('(')[0] + '.log'
#    path = '/apps/px/log/' + logname
#    hosts = rxselect.split('(')[1].strip('()').split(' ')
#    headerList = SearchUtils.searchLog(path, hosts, searchtype, request, logbegin, logend)
#    createHeaderTable(headerList)
#else:
#    logname = 'tx_' + txselect.split('(')[0] + '.log'
#    path = '/apps/px/log/' + logname
#    hosts = txselect.split('(')[1].strip('()').split(' ')
#    headerList = SearchUtils.searchLog(path, hosts, searchtype, request, logbegin, logend)
#    createHeaderTable(headerList)
        
print """
    </td>
  </tr>
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
  <!-- end body -->
</center>
</body>
</html>
"""
