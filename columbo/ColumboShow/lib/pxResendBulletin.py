#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: pxResendBulletin.py
#
# Author: Dominik Douville-Belanger
#
# Description: Uses pxResend to resend bulletins
#
# Date: 2006-08-21 (new updated version)
#
#############################################################################################

import cgi
import cgitb; cgitb.enable()
import sys, os, commands

sys.path.append("/apps/px/lib")
import PXPaths; PXPaths.normalPaths()
from ConfReader import ConfReader

cr = ConfReader("%spx.conf" % (PXPaths.ETC))
user = cr.getConfigValues("user")[0]

def showAlert(msg):
    msg = msg.replace("\n", "\\n") # Javascript needs explicit line breaks
    print """
        <script type="text/javascript">
            alert('%s')
            window.close()
        </script>
    """ % (msg)

form = cgi.FieldStorage()

print "Content-Type: text/html"
print
 
print """
<html>
<head>
<meta name="Author" content="Dominik Douville-Belanger">
<meta name="Description" content="Resend a bulletin file">
<meta name="Keywords" content="">
<link rel="stylesheet" type="text/css" href="/css/style.css">
</head>
<body bgcolor="#cccccc">
<div align="center">
""" 

if form.has_key("flows"):
    flows = form["flows"].value
    if " " in flows:
        showAlert("Your flow list must not contain spaces.")
    else:
        if form.has_key("rsall") or form.has_key("bulletins"):
            if form.has_key("rsall"):
                bulletins = form["all"].value.split(" ")
            else:
                if type(form["bulletins"]) is list:
                    bulletins = [bulletin.value for bulletin in form["bulletins"]]
                else:
                    bulletins = [form["bulletins"].value]
               
            # We write all the lines to a temporary file.
            # This way we do not exceed the command-line maximum length
            tmpfilePath = "/tmp/pxResendInput.txt"
            tmpfile = open(tmpfilePath, "w")
            
            for bulletin in bulletins:
                tmpfile.write("%s\n" % (bulletin))
            tmpfile.close()

            scriptPath = "/apps/px/lib/search/pxResend.py -d %s < %s" % (flows, tmpfilePath)
            command = "sudo -u %s %s" % (user, scriptPath)
            status, output = commands.getstatusoutput(command)
            os.remove(tmpfilePath)
            showAlert(output) # This is the good alert.
        else:
            showAlert("Choose one or more bulletin file to resend.")
else:
    showAlert("You must enter one more more destination flows.")

print"""
</div>
</body>
</html>
"""
