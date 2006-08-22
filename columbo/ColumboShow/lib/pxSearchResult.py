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
#              the results. This version is now independent from SearchUtils, it uses
#              a command-line program to do the dirty work instead.
#
# Date: 2006-08-15 (new updated version)
#
# TODO: Make the command path-independent (the executable must be in the PATH)
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

form = cgi.FieldStorage()

def createDisplayTable(results):
    print """
    <div align="center">
    <h2><b>%s bulletins found</b></h2>
    """ % (len(results))

    # This part only shows if the search process found something
    if len(results) > 0:
        print """
        <form method=POST action="pxResendBulletin.py" target="_blank">
        <input type="hidden" name="all" value="%s">
        <input type="submit" name="rschecked" value="Resend Checked">&nbsp;&nbsp;<input type="submit" name="rsall" value="Resend All">&nbsp;&nbsp;<input type="reset" value="Reset">
        <br><br>
        Flows: <input type="text" name="flows" size="60"> <i>(comma separated list)</i>
        </div>
        <br>
        <table border="2" align="center">
            <tr>
                <td>
                    <b>Resend</b>
                </td>
                <td valign="top" align="center" bgcolor="#cccccc">
                    <b>Header File</b>
                </td>
            </tr>
        """ % (" ".join(results))

        for result in results:
            print """
            <tr>
                <td align="center">
                    <input type="checkbox" name="bulletins" value="%s">
                </td>
                <td valign="top" align="left" bgcolor="#cccccc">
                    <a href="pxBulletinDetails.py?item=%s" target="_blank">%s</a>
                </td>
            </tr>
            """ % (result, result, result) # Checkbox value, URL, link name
    
    print """
    </table>
    </form>
    """
    
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

command = "sudo -u pds /apps/px/lib/search/pxSearch.py " # TEMPORARY
#command = "" # Uncomment this when the above solution isn't necessary anymore

searchType = form["type"].value
if searchType == "tx":
    command += "--tx "
    if type(form["senders"]) is list:
        startFlows = [sender.value for sender in form["senders"]]
    else:
        startFlows = [form["senders"].value]
elif searchType == "rx":
    command += "--rx "
    if type(form["receivers"]) is list:
        startFlows = [receiver.value for receiver in form["receivers"]]
    else:
        startFlows = [form["receivers"].value]
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

# Setting search criterias
if form.has_key("ttaaii"):
    command += "-t %s " % (form["ttaaii"].value)
if form.has_key("ccccxx"):
    command += "-c %s " % (form["ccccxx"].value)
if form.has_key("ddhhmm"):
    command += "-d %s " % (form["ddhhmm"].value)
if form.has_key("bbb"):
    command += "-b %s " % (form["bbb"].value)
if form.has_key("stn"):
    command += "-s %s " % (form["stn"].value)
if form.has_key("seq"):
    command += "-q %s " % (form["seq"].value)
if form.has_key("srcdest"):
    command += "-g %s " % (form["srcdest"].value)
if form.has_key("prio"):
    command += "-p %s " % (form["prio"].value)

if form.has_key("timesort"):
    command += "--timesort "

# Completing the command
command += " ".join(startFlows)
#print "<b>DEBUG:</b> %s" % (command) # <------------------------------------------ DEBUG
#print "<br><br>"

status, output = commands.getstatusoutput(command)
if not status:
    createDisplayTable(output.splitlines())
else:
    print status, output # Something went wrong

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
