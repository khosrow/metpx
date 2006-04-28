#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: resendBulletin.py
#
# Author: Dominik Douville-Belanger (CMC Co-op student)
#
# Description: Resend a bulletin file
#
# Date: 2005-07-11
#
#############################################################################################

import cgi
import cgitb; cgitb.enable()
import sys, os, pwd, time, re, pickle, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from PDSPath import *
from ColumboPath import *
from types import *
from myTime import *
from ConfigParser import ConfigParser
from Logger import Logger

config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
action_logname = config.get('LOG', 'action_log')

logger = Logger(action_logname, "INFO", "AL")
logger = logger.getLogger()

form = cgi.FieldStorage()
destination = form["destination"].value
dbpath = form["dbpath"].value
host = form["host"].value

if destination == "amis":
    status, output = commands.getstatusoutput('sudo -u pds /usr/bin/ssh %s /apps/px/bin/pxSender amis reload' % host)

print "Content-Type: text/html"
print
 
print """<html>
<head>
<meta name="Author" content="Dominik Douville-Belanger">
<meta name="Description" content="Resend a bulletin file">
<meta name="Keywords" content="">
<link rel="stylesheet" type="text/css" href="/css/style.css">
<style>
</style>
</head>
""" 

oldname = dbpath.split('/')[-1]
tmp = oldname.split(':')
tmp[1] = "columbopx-retransmit"
newname = ':'.join(tmp)

currentsec = time.gmtime()
hour = time.strftime("%Y%m%d%H", currentsec)
copypath = '/apps/px/txq/%s/2/%s' % (destination, hour)
# We make sure the queue directory is created.
mkdircommand = "sudo -u pds /usr/bin/ssh %s mkdir %s" % (host, copypath)
status, output = commands.getstatusoutput(mkdircommand)

command = 'sudo -u pds /usr/bin/ssh %s cp %s %s' % (host, dbpath, copypath + '/' + newname)
status, output = commands.getstatusoutput(command)
if status:
    logger.info("Bulletin Resender: sending %s to %s on %s -> FAIL" % (oldname, destination, host))
else:
    logger.info("Bulletin Resender: sending %s to %s on %s -> OK" % (oldname, destination, host))

print"""
<script language="JavaScript">
    window.close();
</script>

</html>
"""
