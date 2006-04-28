#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pdsClientInfosTab.py
#
# Author: Daniel Lemay
#
# Date: 2004-10-18
#
# CCS = Columbo Crime Scene (Each Individual PDS is a crime scene)
# CIR = Columbo Investigation Room (Investigation Room is on a LVS, clues are merged in results)
# CS  = Columbo Show (The Show is on a LVS)
#
# Description: Page that gives detailed (coming for each PDS) informations  about a PDS client.
# The two main tasks are:
#
# 1) Read the "results" file sent by CIR host.
# 2) Present the last log on each PDS
# 3) Give the possibility of toggling a client
# 4) Search tool
# 5) Present results of the search
#
#############################################################################################
import cgi
import cgitb; cgitb.enable()
import sys, os, pwd, time, re, pickle, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from PDSPath import *
from ColumboPath import *
from CompositePDSClient import CompositePDSClient
from CompositePDSInputDir import CompositePDSInputDir
from ConfigParser import ConfigParser
from Logger import Logger
from JSMaker import JSMaker
from types import *
from myTime import *
import template

def unarchiveResults(filename):
   file = open(filename, "rb")
   compositeClientDict = pickle.load(file)
   compositeInputDirDict = pickle.load(file)
   file.close()
   return compositeClientDict, compositeInputDirDict

def unarchiveListing(filename):
   file = open(filename, "rb")
   listingDict = pickle.load(file)
   file.close()
   return listingDict

# Read configuration file
config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
results_name = config.get('CIR', 'results_name')   # How the "results" file will be named (path not included)
logname = config.get('CS', 'logname')              # Full name for the logfile
log_level = config.get('CS', 'log_level')          # Level of logging
host = config.get('CCS', 'host')                   # Where the program to create a client listing must be initiated
timeout = int(config.get('CS', 'results_timeout')) # Number of minutes after which the "results" are considered outdated

# If not defined in configuration file, set defaults
if (not logname ):
   logname = CS + "/log/" + "CS.log"
if (not log_level):
   log_level = "DEBUG"

# Enable logging
logger = Logger(logname, log_level, "CS")
logger = logger.getLogger()

#############################################################################################
# 1) Read the "results" file sent by CIR host.
#############################################################################################
clientDict, inputDirDict = unarchiveResults(INPUT_RESULTS + "/" + results_name)

js = JSMaker()
js.createMaxers(clientDict, inputDirDict)

form = cgi.FieldStorage()
clientName = form["client"].value
listingOn = int(form["listing"].value)
machines = clientDict[clientName].getHosts()

logger.info("Execution of clientInfosTab.py page for " + clientName)

# Initialisation of form entries
if (form.has_key("glob")):
   glob = form["glob"].value
else:
   glob = ""

if (form.has_key("endDate")):
   endDate = form["endDate"].value
   epochEndDate = int(convertToEpoch(endDate))
else:
   epochEndDate = int(now())
   endDate = epochFormatted(epochEndDate)

if (form.has_key("startDate")):
   startDate = form["startDate"].value
   epochStartDate = int(convertToEpoch(startDate))
else:
   epochStartDate = int (epochEndDate - 4 * HOUR)
   startDate = epochFormatted(epochStartDate)

if (form.has_key("maxFiles")):
   maxFiles = form["maxFiles"].value
else: 
   maxFiles = ""

machinesString = ','.join(machines)

TOOLONG = 1000      # If  the length of the listing is greater than TOOLONG, different treatment (no javascript sorting)
listingTooLong = 1  # Will be changed to 0 if listing is less than TOOLONG
lenListingDict = -1 # Implies the length has not been taken

#############################################################################################
# 2) Present (HTML) the last log on each PDS
#############################################################################################

print "Content-Type: text/html"
print
 
#print "Machines " + machinesString
print """<html>
<head>
<meta name="Author" content="Daniel Lemay">
<meta name="Description" content="Queue repartition">
<meta name="Keywords" content="">
<title>Queue repartition </title>
<link rel="stylesheet" type="text/css" href="/css/style.css">
<style>
</style>
<script type="text/javascript">
// Put data concerning the PDSs in a javascript array
"""
js.createJSArrayRepartition(clientDict, clientName)
   
if (listingOn):
   listingDict = unarchiveListing(INPUT_RESULTS + "/" + clientName + "_listing")
   lenListingDict = len(listingDict)
   if (lenListingDict <= TOOLONG): # If listing is not too long, we will create a JS Array => we will be able to sort online
      js.createJSArrayListing(listingDict)
      listingTooLong = 0

print """

function confirmResend(){
   if (confirm("Are you sure you want to resend this product?")) {
      return true;
   } else {
      return false;
   }
}
</script>
<script src="/js/calendar1.js"></script>
<script src="/js/calendar2.js"></script>
<script src="/js/SortableTable.js"></script>
<!--<script src="/js/liveclock.js"></script>-->
<script src="/js/windowUtils.js"></script>
</head>
""" 

keys = clientDict.keys()
keys.sort(lambda x,y: cmp(y,x))

headers = ["""<a href="#" title="Sort by Machine" onclick="clientTable.sort(0); drawTable(clientInfos, 'client_body'); return false;">Machine</a>""",
           """<a href="#" title="Sort by Quantity" onclick="clientTable.sort(1); drawTable(clientInfos, 'client_body'); return false;"> Queue </a>""",
           """<a href="#" title="Sort by timestamp" onclick="clientTable.sort(2); drawTable(clientInfos, 'client_body'); return false;">Last Log Line  </a>""", 
           """<a href="#" title="Cannot sort by this">Date</a>""",
           """<a href="#" title="Cannot sort by this">Status</a>"""]
                 
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

  <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
      <br>
      <!--
      <script type="text/javascript"> 
      new LiveClock('arial', '2', '#000000', '#ffffff', 'UTC Time: ', '', '300', '0', '', '', '', 0);
      LC_InitializeClocks();
      </script>
      -->
"""
print """
      <h1>Client: %s (<a href="javascript:popIt('/etc/%s.conf');">Configuration file</a>, <a href="javascript:popIt('/etc/pdstable');">Operations PDS table</a>, <a href="javascript:popIt('/etc/PDSLIST');">PDSLIST</a>)</h1>
    </td>
  </tr>

  <tr>
    <td valign="top" bgcolor="#cccccc">
      <center>
""" % (clientName, clientName) 

lastResultsInSeconds = os.stat(INPUT_RESULTS + "/" + results_name)[8]
lastResultsDate = time.strftime("%a %b %d %H:%M:%S %Y", time.gmtime(lastResultsInSeconds))
now = time.time()

if now - (timeout * 60) > lastResultsInSeconds:
   print "Last results: <b><font color=RED size=4>%s %s</font></b>" % (lastResultsDate, '(outdated)')
else:
   print "Last results: <font size=3>%s</font>" % (lastResultsDate)

js.staticHtmlForTable("infos", "client_body", headers)

print """
      </center>
      <br>
<script type="text/javascript">
var colTypes = ["ALPHABETIC", "NUMERIC", "ALPHABETIC"];
var orderStatus = [1, 0, 0];
var clientTable = new SortableTable(colTypes, orderStatus, clientInfos);
clientTable.sort(0);
drawTable(clientInfos, "client_body");
</script>
    </td> 
  </tr>  
  <!-- end body -->

  <!-- Begin form -->
  <tr>
    <td valign="top" align="center" bgcolor="#cccccc">
      <table>
        <tr>
          <td>
            <form>
"""
#############################################################################################
# 3) Give the possibility of toggling a client
#############################################################################################
print """<input type="button" name="toggle" value="Toggle Client State" onClick="location='%s'">""" % ("pdsToggleClient.py?client=" + clientName + "&machines=" + machinesString)
          
print """
            </form>
          </td>
        </tr>
      </table>
    </td>
  </tr>
  <!-- End form -->
  
  <tr>
    <td>
    <fieldset>
    <legend>Resending tool</legend>
      <table width="100%">

        <tr>
          <td>
            <table align="center" cellpadding="3" cellspacing="0" border="0" width="100%" bgcolor="#cccccc">
             <!--
              <tr>
                <td align="center"><h1>Resending Tool</h1></td>
              </tr>
              -->
             
              <tr>
                <td  align="center">			
                  <table cellpadding="5" cellspacing="1" width="1100" border="0">
                    <tr>
                      <th colspan="4" class="header" bgcolor="#326696"><font color="white" face="tahoma, verdana" size="2">Use the search tool to obtain a list of files you could resend</font></th>
                    </tr>

                    <form name="listing" action="pdsGetClientListing.py" method="post">
"""
print """

                    <tr>
                      <td bgcolor="#ffffff" valign="top" width="300">
                         Pattern to match:<br>
                        <input type="text" name="glob"  size="40" value="%s">
                      </td>

                      <td bgcolor="#ffffff" valign="top">
                        Starting Date:<br>
                        <input type="Text" name="startDate" value="%s">
                        <a href="javascript:cal1.popup();"><img src="/js/img/cal.gif" width="16" height="16" border="0" alt="Click Here to Pick up the date"></a><br>
                      </td>
                      <td bgcolor="#ffffff">
                        Ending Date:<br>
                        <input type="Text" name="endDate" value="%s">
                        <a href="javascript:cal2.popup();"><img src="/js/img/cal.gif" width="16" height="16" border="0" alt="Click Here to Pick up the date"></a><br>
                      </td>

                      <td bgcolor="#ffffff" valign="top">
                         Max. Number of files:<br>
                         <input type="hidden" name="maxFiles" value="%s">

                      </td>
                    </tr>

""" % (glob, startDate, endDate, maxFiles)

print """
                    <script language="JavaScript">
                    <!-- // create calendar object(s) just after form tag closed
                    // specify form element as the only parameter (document.forms['formname'].elements['inputname']);
                    // note: you can have as many calendar objects as you need for your application
                    var cal1 = new calendar1(document.forms['listing'].elements['startDate']);
                    cal1.year_scroll = true;
                    cal1.time_comp = true;
                    var cal2 = new calendar1(document.forms['listing'].elements['endDate']);
                    cal2.year_scroll = false;
                    cal2.time_comp = true;
                    //-->
                    </script>
"""
print """
                    <tr>
                      <td align="center" colspan="4" class="client_row" bgcolor="#DBEAF5">
                        <input type="hidden" name="clientName" value="%s">
                        <input type="hidden" name="machinesString" value="%s">
                        <input type="hidden" name="host" value="%s">
                        <input type="submit" name="" value="Submit/Refresh Search"></td>
                    </tr>
                    </form>
""" % (clientName, machinesString, host)

print """
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>

  <!-- Begin Table containing files to resend --> 
        <tr>
          <td align="center" valign="top" bgcolor="#cccccc">
            <table summary="" cellpadding="0" cellspacing="0" align="center" title="" width="1100" border="0" bgcolor="white">
              <tr>
                <td>
                  <table summary="" cellpadding="0" cellspacing="0" width="100%" align="center" border="0">
"""

if (lenListingDict >= 0):                   
   print """
                    <tr class="header" bgcolor="gray"> <td colspan="3" align="center"><b><font color="white">Files you could resend (matching your search criterias): %d files</font></b></td> </tr>

""" % (lenListingDict)
   print """
                    <tr class="header"  bgcolor="silver">
                      <td width="16%"><font color="white">Timestamp</font></td>
                      <td width="80%"><font color="white">Name</font></td>
                      <td width="4%"></td>
                    </tr>
"""

elif (lenListingDict < 0):
   print """
                    <tr class="header" bgcolor="gray"> <td colspan="3" align="center"><b><font color="white">Files you could resend (matching your search criterias)</font></b></td> </tr>
                    <tr class="header" bgcolor="silver">
                      <td width="16%"><font color="white">Timestamp</font></td>
                      <td width="80%"><font color="white">Name</font></td>
                      <td width="4%"></td>
                    </tr>
"""
print """
                  </table> 
                </td>
              </tr>

              <tr>
                <td>
                  <div style="width:100%; overflow:auto; height:300px;"> 
"""

if (not listingTooLong or (not listingOn)):

   js.makeHtmlListingTable("listing_table", "listing_body")
   if (listingOn):
      print """
<script type="text/javascript">
var listing_colTypes = ["ALPHABETIC", "ALPHABETIC"];
var listing_orderStatus = [1, 1 ];
var listingTable = new SortableTable(listing_colTypes, listing_orderStatus, listing);
listingTable.sort(1)
drawTable(listing, "listing_body");
</script>
"""
else: # listing is on and the list is too long
   print "<table cellpadding='0' cellspacing='0' bgcolor='white'>"
   for file in listingDict.keys():
      # This trick has been introduced because of problem with HTML tables containing long word
      if (len(file) > 100):
         reduceFilename = file[:40] + "\n" + file[40:]
         print "<tr><td width='16%' class='beige_row' align='left' " + ">%s</td>" % (listingDict[file][1]) + "<td width='80%'" + " class='beige_row' align='left'><a href='pdsResendFile.py?client=%s" % (clientName) + "&filename=%s' onClick='return confirmResend()'>%s</a></td></tr>" % (file, reduceFilename)
      else:
         print "<tr><td width='16%' class='beige_row' align='left' " + ">%s</td>" % (listingDict[file][1]) + "<td width='80%'" + " class='beige_row' align='left'><a href='pdsResendFile.py?client=%s" % (clientName) + "&filename=%s' onClick='return confirmResend()'>%s</a></td></tr>" % (file, file)
   print "</table>"

print """
                  </div>
                </td>
              </tr>
            </table>
           <br><br>
          </td>
        </tr>

      </table>
      </fieldset>
    </td>
  </tr>

  <!-- End Resending Section --> 
      
  <!-- Begin footer menu --> 
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
  <!-- End footer menu --> 

</table>
</center>

"""
print "</body>"
print "</html>"
