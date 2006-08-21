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
import sys, os, pwd, time, re, pickle, commands
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

sys.path.append("/apps/px/lib/search")

def showAlert(msg):
    print """
        <script type="text/javascript">
            alert(%s)
            window.close()
        </script>
    """ % (msg)
    sys.exit(1)

form = cgi.FieldStorage()

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

if form.has_key("flows"):
    flows = form["flows"].value
    if " " in flows:
        showAlert("'Your flow list must not contain spaces.'")
else:
    showAlert("'You must enter one more more destination flows.'")    
    
if form.has_key("rsall"):
    bulletins = form["all"].value.split(" ")
else:
    if form.has_key("bulletins"):
        if type(form["bulletins"]) is list:
            bulletins = [bulletin.value for bulletin in form["bulletins"]]
        else:
            bulletins = [form["bulletins"].value]
    else:
        showAlert("'Choose one or more bulletin file to resend.'")

# Dumper les bulletins dans un fichier temporaire.

command = "/apps/px/lib/search/pxResend.py -d %s" % (flows)

print"""
<script language="JavaScript">
    window.close();
</script>

</html>
"""
