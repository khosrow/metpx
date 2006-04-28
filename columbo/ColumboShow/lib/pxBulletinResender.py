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
# Author: Dominik Douville-Belanger (CMC Co-op student)
#
# Description: Web page for searching bulletin files
#
# Date: 2005-05-10
#
#############################################################################################

import cgi
import cgitb; cgitb.enable()
import sys, os, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from PDSPath import *
from ColumboPath import *
from types import *
from myTime import *
from ConfigParser import ConfigParser
from Logger import Logger
import template

import SearchUtils

config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
action_logname = config.get('LOG', 'action_log')
backends = config.get('CIR', 'backends').split(' ')
frontend = config.get('CIR', 'frontend').split(' ') # We keep it in a list since it can easily be added to backends

def getLogNames(type):
    """
    Creates a list of all available logs to search from
    Arguments:
        type -> 'tx' or 'rx'
    Returns: a list of strings
    """
    result = []
    
    if len(backends) == 0:
        return []
    
    # Determines if the log is associated to an active client of the right type 
    possible = SearchUtils.possibleLog(backends[0], type)
    backendStatus, backendContent = commands.getstatusoutput('sudo -u pds /usr/bin/ssh ' + backends[0] + ' "ls /apps/px/log/' + type + '_*.log"') # Get all tx or rx logs
    if backendStatus == 0:
        # Extract only the client name from the log (/apps/px/log/tx_test.log becomes test)
        backendContent = map(lambda x: x.split('/')[-1].split('_')[-1].replace('.log', ''), backendContent.splitlines())
        # Add ' (backend) to the log name if the log is a possible choice
        result += [bc + '(%s)' % (' '.join(backends)) for bc in backendContent if bc in possible]
   
    # Same thing for the frontend
    if len(frontend) == 0:
        return []
    else:
        possible = SearchUtils.possibleLog(frontend[0], type)
        frontendStatus, frontendContent = commands.getstatusoutput('sudo -u pds /usr/bin/ssh ' + frontend[0] + ' " ls /apps/px/log/' + type + '_*.log"') # Get all tx or rx logs
        if frontendStatus == 0:
            frontendContent = map(lambda x: x.split('/')[-1].split('_')[-1].replace('.log', ''), frontendContent.splitlines())

        result += [fc + '(%s)' % (' '.join(frontend)) for fc in frontendContent if fc in possible]
    
    return result

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
<meta name="Description" content="Resending Tool">
<meta name="Keywords" content="">
<META HTTP-EQUIV="Pragma" CONTENT="no-cache">
<META HTTP-EQUIV="Expires" CONTENT="-1">
<title>Bulletin Search & Send</title>
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

print """
  <tr>
    <td valign="top" bgcolor="#cccccc">
        <!-- HERE BEGINS THE MAIN BODY OF THE PAGE -->
        <form method=POST action="pxSearchResult.py" target="_blank">
            <table bgcolor="#cccccc" border="0" cellpadding="0" cellspacing="5">
                <tr>
                    <td><h3><u>Search From:</u></h3></td>
                </tr>
                <tr>
                    <td><input type="radio" name="searchtype" value="rx" CHECKED>pxReceiver logs</td>
                    <td><select name="rxselect"><!--<option value="all(backend)">all (backend)<option value="all(frontend)">all (frontend)-->%s</select></td>
                    <br>
                </tr>
                <tr>
                    <td><input type="radio" name="searchtype" value="tx">pxSender logs</td>
                    <td><select name="txselect"><!--<option value="all(backend)">all (backend)<option value="all(frontend)">all (frontend)-->%s</select></td>
                    <br>
                </tr>
                <tr>
                    <td><input type="radio" name="searchtype" value="dbfrontend" DISABLED>DB %s</td>
                </tr>
                <tr>
                    <td><input type="radio" name="searchtype" value="dbbackends" DISABLED>DB %s</td>
                </tr>
            </table>
            <table bgcolor="#cccccc" border="0" cellpadding="0" cellspacing="5">
                <tr>
                    <td><h3><u>Search critieria:</u></h3></td>
                </tr>
                <tr>
                    <td align=center>TTAAii</td>
                    <td align=center>CCCCxx</td>
                    <td align=center>DDHHMM</td>
                    <td align=center>BBB</td>
                    <td align=center>STN</td>
                    <td align=center>SRC (Senders and DB)</td>
                    <td align=center>DST (Receivers)</td>
                    <td align=center>SEQ#</td>
                    <td align=center>PRIO#</td>
                    <td align=center>From YYYYMMDDHH</td>
                    <td align=center>To YYYYMMDDHH</td>
                </tr>
                <tr>
                    <td align=center><input type="text" name="ttaaii" size="8" maxlength="8"></td>
                    <td align=center><input type="text" name="ccccxx" size="8" maxlength="8"></td>
                    <td align=center><input type="text" name="ddhhmm" size="6" maxlength="6"></td>
                    <td align=center><input type="text" name="bbb" size="6" maxlength="3"></td>
                    <td align=center><input type="text" name="stn" size="6" maxlength="5"></td>
                    <td align=center><input type="text" name="src" size="20" maxlength="20"></td>
                    <td align=center><input type="text" name="dst" size="20" maxlength="20"></td>
                    <td align=center><input type="text" name="seq" size="6" maxlength="5"></td>
                    <td align=center><input type="text" name="prio" size="2" maxlength="2"></td>
                    <td align=center><input type="text" name="frommdh" size="10" maxlength="10"></td>
                    <td align=center><input type="text" name="tomdh" size="10" maxlength="10"></td>
                </tr>
                <tr>
                </tr>
                <tr>
                    <td>
                        <input type="submit" value="Search">
                        &nbsp;&nbsp;
                        <input type="reset" value="Reset">
                    </td>
                </tr>
                <tr>
                    <td>
                        <br>
                        Fields that accept *:
                        <ul>
                            <li type="disc">TTAAii
                            <li type="disc">CCCCxx
                            <li type="disc">BBB
                            <li type="disc">STN
                            <li type="disc">SRC
                            <li type="disc">SEQ#
                        </ul>
                    </td>
                </tr>
            </table>
        </form>
    </td>
  </tr>
  <!-- end body -->
""" % (menuContent('rx'), menuContent('tx'), ' '.join(backends), ' '.join(frontend))
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
