#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: BulletinResender.py
#
# Author: Dominik Douville-Belanger
#
# Description: Web page to search & resend bulletin files
#
# Date: 2006-08-15 (new updated version)
#
#############################################################################################

import cgi
import cgitb; cgitb.enable()
import sys, os, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")
sys.path.append("/apps/px/lib")

from PDSPath import *
from ColumboPath import *
from types import *
from myTime import *
from ConfigParser import ConfigParser
import PXPaths; PXPaths.normalPaths()
import template

# Quick way to read from a file, strip each EOL and put it all in a list
targets = [target.strip() for target in open("%spxSearch.targets" % (PXPaths.ETC), "r").readlines()]

def getLogNames(type):
    """
    Gets the name of all logs on the target machines
    Arguments:
        type -> 'tx' or 'rx'
    Returns: a list of string
    """
    logNames = []
    for target in targets:
        status, output = commands.getstatusoutput('sudo -u pds ssh %s "ls -1 %s%s_*.log"' % (target, PXPaths.LOG, type))
        if status == 0:
            lines = output.splitlines()
            logNames += [line.split("_")[-1].split(".")[0] for line in lines if line.split("_")[-1].split(".")[0] not in logNames] # We take out the tx_ (or _rx) and the .log parts
    logNames.sort()
    return logNames

def menuContent(type):
    """
    Creates the menu options dynamically
    Arguments:
        type -> 'tx' or 'rx'
    Returns: a string
    """

    result = ''
    names = getLogNames(type)
    for name in names:
        result += '<option value="%s">%s ' % (name, name)
    return result

# Beginning the HTML generation code

print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Dominik Douville-Belanger">
<meta name="Description" content="Search and Resend web interface">
<meta name="Keywords" content="">
<META HTTP-EQUIV="Pragma" CONTENT="no-cache">
<META HTTP-EQUIV="Expires" CONTENT="-1">
<title>Bulletins Search & Resend</title>
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

"""

# Here begins the main body of the page
print """
  <tr>
    <td valign="top" bgcolor="#cccccc">
        <form method=POST action="pxSearchResult.py" target="_blank">
            <h2><u>Search:</u></h2>
            <h3>Type:</h3>
            <table bgcolor="#cccccc" border="0" cellpadding="0" cellspacing="5">
                <tr>
                    <td valign="top">
                        <input type="radio" name="type" value="tx" CHECKED>Senders:
                    </td>
                    <td>
                        <select multiple="true" name="senders" size="4">
                        %s
                        </select>
                    </td>
                </tr>
                <tr>
                    <td valign="top">
                        <input type="radio" name="type" value="rx">Receivers:
                    </td>
                    <td>
                        <select multiple="true" name="receivers" size="4">
                        %s
                        </select>
                    </td>
                </tr>
            </table>
            
            <h3>Filter:</h3>
            <table bgcolor="#cccccc" border="0" cellpadding="0" cellspacing="5">
                <tr>
                    <td>
                        <input type="radio" name="filter" value="none" CHECKED>None
                    </td>
                </tr>
                <tr>
                    <td>
                        <input type="radio" name="filter" value="since">Since the last <input type="text" name="sinceinput" size="4" maxlength="4"> hours
                    </td>
                </tr>
                <tr>
                    <td>
                        <input type="radio" name="filter" value="boundaries">From: <input type="text" name="frominput" size="14" maxlength="14"> To: <input type="text" name="toinput" size="14" maxlength="14"> <i>(YYYYMMDDHHmmSS)</i>
                    </td>
                </tr>
            </table>

            <h3>Criterias:</h3>
            <i>Example: SACN31_CWAO_151300__CYXX_75340:ncp2:CWAO:SA:3:Direct:20060815130152</i>
            <table bgcolor="#cccccc" border="0" cellpadding="0" cellspacing="5">
                <tr>
                    <td align="center">TTAAii <i>(SACN31)</i></td>
                    <td align="center">CCCCxx <i>(CWAO)</i></td>
                    <td align="center">DDHHMM <i>(151300)</i></td>
                    <td align="center">BBB <i>()</i></td>
                </tr>
                <tr>
                    <td><input type="text" name="ttaaii" size="20" maxlength="20">
                    <td><input type="text" name="ccccxx" size="20" maxlength="20">
                    <td><input type="text" name="ddhhmm" size="20" maxlength="20">
                    <td><input type="text" name="bbb" size="20" maxlength="20">
                </tr>
                <tr>
                    <td align="center">STN <i>(CYXX)</i></td>
                    <td align="center">SEQ # <i>(75340)</i></td>
                    <td align="center">SRC/DEST <i>(ncp2)</i></td>
                    <td align="center">PRIORITY <i>(3)</i></td>
                </tr>
                <tr>
                    <td><input type="text" name="stn" size="20" maxlength="20">
                    <td><input type="text" name="seq" size="20" maxlength="20">
                    <td><input type="text" name="srcdest" size="20" maxlength="20">
                    <td><input type="text" name="prio" size="20" maxlength="20">
                </tr>
            </table>
            
            <br>
            <input type="checkbox" name="timesort" value="timesort">Sort by timestamps
            <br>
            
            <br>
            <table bgcolor="#cccccc" border="0" cellpadding="0" cellspacing="5">
                <tr>
                    <td>
                        <input type="submit" value="SEARCH">
                    </td>
                    <td>
                        <input type="reset" value="RESET">
                    </td>
                </tr>
            </table>
        </form>
    </td>
  </tr>
  <!-- end body -->
""" % (menuContent("tx"), menuContent("rx"))

# Page footer
print """
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
print '<head><META HTTP-EQUIV="Pragma" CONTENT="no-cache"><META HTTP-EQUIV="Expires" CONTENT="-1"></head>'
print "</html>"
