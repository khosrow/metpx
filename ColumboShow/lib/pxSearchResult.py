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
# Author: Dominik Douville-Belanger (CMC Co-op student)
#
# Description: Parse the entries of the search form and show the results.
#
# Date: 2005-05-02
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
from ConfigParser import ConfigParser

import SearchUtils
import HeaderInfo

class InvalidDirection(Exception): pass

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

NUM = r'[[:digit:]]+'
STR = r'[[:alnum:]-]+'
STR2 = r'[-[:alnum:]_]+' # Used once you pass the first ':' delimiter so it includes '_'
GSTR = r'[[:alnum:]-]*_?' # Ghost string: May or may not be there

searchtype = form["searchtype"].value
rxselect = form["rxselect"].value
txselect = form["txselect"].value

# Default values used to locate the logs
starttime = NUM
logbegin = time.gmtime(0)
stoptime = NUM
logend = time.gmtime(0)

if form.has_key("ttaaii"):
    ttaaii = SearchUtils.wildCardCheck(form["ttaaii"].value)
else:
    ttaaii = STR

if form.has_key("ccccxx"):
    ccccxx = SearchUtils.wildCardCheck(form["ccccxx"].value)
else:
    ccccxx = STR

if form.has_key("ddhhmm"):
    ddhhmm = form["ddhhmm"].value
else:
    ddhhmm = NUM

if form.has_key("bbb"):
    bbb = SearchUtils.wildCardCheck(form["bbb"].value + '_')
else:
    bbb = GSTR
    
if form.has_key("stn"):
    stn = SearchUtils.wildCardCheck(form["stn"].value + '_')
else:
    stn = GSTR

if form.has_key("src"):
    src = SearchUtils.wildCardCheck(form["src"].value)
else:
    src = STR2

if form.has_key("dst"):
    dst = form["dst"].value
else:
    dst = STR2

if form.has_key("seq"):
    seq = SearchUtils.wildCardCheck(form["seq"].value)
else:
    seq = NUM

if form.has_key("prio"):
    prio = form["prio"].value
else:
    prio = NUM

if form.has_key("frommdh"):
    try: # In case this is not the right format
        starttime = form["frommdh"].value
        logbegin = time.strptime(starttime, '%Y%m%d%H')
    except ValueError:
        pass # Value already set
if form.has_key("tomdh"):
    try:
        stoptime = form["tomdh"].value
        logend = time.strptime(stoptime, '%Y%m%d%H')
    except ValueError:
        pass # Value already set

#################################################################
# THE PROBLEM WITH THE BBB AND STN FIELDS (KNOWN AS THE 50 BUG) #
#################################################################
"""
Why do we get false results when we do a search with only a sequence
number or 50 (or whatever other number)?
This problem occurs because of the nature or the BBB and STN fields.
In some bulletin filename, they may or may not be there.
Example:
    SACN48_CWAO_202000_86602:tandem:CWAO:SA:3:Direct:20050720200055 (No BBB or STN)
    SACN48_CWAO_201900_CCA_85219:tandem:CWAO:SA:3:Direct:20050720192246 (A BBB no STN; the opposite could also be true)
We do not know when this will happen. A log or the DB may contain more than one sort or entry.
We must then construct a regular expression that matches both cases.
In this egrep regular expression we use strings ([[:alnum:]-]+), digits ([[:digit:]]+) and the source
of the problem, the so called Ghost Strings ([[:alnum:]-]*_?). The BBB and STN fields, when left blank, are represented
by Ghost Strings. So if we look at this part of the regex it looks like this: 
_[[:alnum:]-]*_?[[:alnum:]-]*_?[[:digit:]]+
     BBB            STN            SEQ
Let's say we are looking for bulletin with a header with a sequence number of 602 but no BBB or STN are specified; we get the
following regex as a result: _[[:alnum:]-]*_?[[:alnum:]-]*_?602
During our search we encounter this header line: SACN48_CWAO_202000_86602:tandem:CWAO:SA:3:Direct:20050720200055
Having not entered any value for the other fields except SEQ, the regex matches for the TTAAii (SACN48), the
CCCCxx (CWAO), the ddhhmm (202000), is there a BBB? No of course not, but the program says YES! In fact the [[:alnum:]-]* matched
the number 8 or the 86602 sequence number, it then sees that there is no '_' but that is okay since the regex says there can or
can't be one (_?). The next 6 does the same trick for the STN and finally the remaining 602 fits our search perfectly. The program
then reports this line as a match to our original query, but it is wrong since we wanted bulletin file with a sequence number
of 602, not containing 602.
At this point I have no idea as to how we can resolve this, especially with egrep limited regular expression capabilities.
Hopefully the query should never returns too little results, it will probably returns too MUCH results. That means that you
should find some good answers inside between all the false one. However this could become a problem if someone decided
to resend all those bulletin at once. Also I fear that this behaviour could cause even weirder results, as I do not know
perfectly egrep search mechanism.
Good luck.
"""

if searchtype == 'rx':
    request = ttaaii + '_' + ccccxx + '_' + ddhhmm + '_' + bbb + stn + seq + ':' + STR2 + ':' + ccccxx + ':' + STR2 + ':' + prio + ':' + STR2 + ':' + NUM 
else:
    request = ttaaii + '_' + ccccxx + '_' + ddhhmm + '_' + bbb + stn + seq + ':' + src + ':' + ccccxx + ':' + STR2 + ':' + prio + ':' + STR2 + ':' + NUM

if searchtype == 'rx' or searchtype == 'tx':
    if searchtype == 'rx':
        logname = 'rx_' + rxselect.split('(')[0] + '.log'
        path = '/apps/px/log/' + logname
        hosts = rxselect.split('(')[1].strip('()').split(' ')
        headerList = SearchUtils.searchLog(path, hosts, searchtype, request, logbegin, logend)
        createHeaderTable(headerList)
    else:
        logname = 'tx_' + txselect.split('(')[0] + '.log'
        path = '/apps/px/log/' + logname
        hosts = txselect.split('(')[1].strip('()').split(' ')
        headerList = SearchUtils.searchLog(path, hosts, searchtype, request, logbegin, logend)
        createHeaderTable(headerList)
        
elif searchtype == 'dbfrontend' or searchtype == 'dbbackends':
    pass # TODO

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
