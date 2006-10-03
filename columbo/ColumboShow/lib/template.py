"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#############################################################################################
# Name: template.py
#
# Author: Daniel Lemay
#
# Date: 2005-08-18
#
# Description:
#############################################################################################
import sys
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from ColumboPath import *
from ConfigParser import ConfigParser

tabs = ['pdsClients', 'pdsSources', 'pxCircuits', 'generalMonitoring',  'admin']

links = {}
links['pdsClients'] = '     <a href="pdsClientsTab.py">PDS Clients</a> |'
links['pdsSources'] = '     <a href="pdsSourcesTab.py">PDS Sources</a> |'
links['pxCircuits'] = '     <a href="pxCircuitsTab.py">PX Circuits</a> |'
links['generalMonitoring'] = '     <a href="generalMonitoringTab.py">General Monitoring</a> |'
links['admin'] = '     <a href="adminTab.py">Administrative Functions</a> |'

states = {}

def openFile(filename, image=1):
    try:
        handle = open(filename)
        return handle
    except IOError:
        # Server redirection to error page
        URL = "missingFile.py?filename=%s&image=%s\n" % (filename, image)
        print 'Location: ', URL

def initStates():
    # Read configuration file
    config = ConfigParser()
    config.readfp(openFile(FULL_MAIN_CONF))

    pdsTab = config.get('PDS', 'tab')
    pxTab = config.get('PX', 'tab')
    generalMonitoringTab = config.get('GM', 'tab')
    adminTab = config.get('ADMIN', 'tab')
    
    # Set all tabs to ON
    for tab in tabs:
        states[tab] = 1
    
    # Check if configuration file set some tabs to 'OFF'
    if pdsTab != 'ON':
        states['pdsClients'] = states['pdsSources'] = 0
    if pxTab != 'ON':
        states['pxCircuits'] = 0
    if generalMonitoringTab != 'ON':
        states['generalMonitoring'] = 0
    if adminTab != 'ON':
        states['admin'] = 0

def pdsClients(color):
    if color == 'grey':
        return """
        <td width="13" align="left" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td width="40" bgcolor="#CCCCCC"><b>PDS<br>Clients</b></td>
        <td width="13" valign="bottom" align ="left"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td valign="bottom"><img src="/images/spacer.jpg" witdh="15"></td>
        <td bgcolor="#FFFFFF" width="15">&nbsp;</td>
         """
    elif color =='blue':
        return """
        <td width="13" align="left" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td width="40" bgcolor="#006699" align="center"><a href="pdsClientsTab.py" class="snav"><b>PDS<br>Clients</b></a></td>
        <td width="13" valign="bottom" align ="left"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td valign="bottom"><img src="/images/spacer.jpg" witdh="15"></td>
        <td bgcolor="#FFFFFF" width="15">&nbsp;</td>
        """
def pdsSources(color):
    if color == 'grey':
        return """
        <td width="13" align="right" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td width="60" bgcolor="#CCCCCC" align="center"><b>PDS<br>Sources</b></td>
        <td width="13" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td bgcolor="#FFFFFF" width="15">&nbsp;</td>
        """
    elif color =='blue':
        return """
        <td width="13" align="right" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td width="60" bgcolor="#006699" align="center"><a href="pdsSourcesTab.py" class="snav"><b>PDS<br>Sources</b></a></td>
        <td width="13" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td bgcolor="#FFFFFF" width="15">&nbsp;</td>
        """
def pxCircuits(color):
    if color == 'grey':
        return """
        <td width="13" align="right" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td width="60" bgcolor="#CCCCCC" align="center"><b>PX<br>Circuits</b></a></td>
        <td width="13" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td bgcolor="#FFFFFF" width="15">&nbsp;</td>
        """
    elif color =='blue':
        return """
        <td width="13" align="right" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td width="60" bgcolor="#006699" align="center"><a href="pxCircuitsTab.py" class="snav"><b>PX<br>Circuits</b></a></td>
        <td width="13" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td bgcolor="#FFFFFF" width="15">&nbsp;</td>
        """
def generalMonitoring(color):
    if color == 'grey':
        return """
        <td width="13" align="right" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td width="64" bgcolor="#CCCCCC" align="center"><b>General<br>Monitoring</b></td>
        <td width="13" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td bgcolor="#FFFFFF" width="15">&nbsp;</td>
        """
    elif color =='blue':
        return """
        <td width="13" align="right" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td width="64" bgcolor="#006699" align="center"><a href="generalMonitoringTab.py" class="snav"><b>General<br>Monitoring</b></a></td>
        <td width="13" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td bgcolor="#FFFFFF" width="15">&nbsp;</td>
        """
def admin(color):
    if color == 'grey':
        return """
        <td width="13" align="right" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td width="70" bgcolor="#cccccc" align="center"><b>Administrative<br>Functions</b></td>
        <td width="13" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td bgcolor="#FFFFFF" width="15">&nbsp;</td>
        """
    elif color =='blue':
        return """
        <td width="13" align="right" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td width="70" bgcolor="#006699" align="center"><a href="adminTab.py" class="snav"><b>Administrative<br>Functions</b></a></td>
        <td width="13" valign="bottom"><img src="/images/whiteRect.gif" width="13" height="40"></td>
        <td bgcolor="#FFFFFF" width="15">&nbsp;</td>
        """

def tabsLine(greyTab=None):
    if states == {}: initStates()
    for tab in tabs:
        if tab == greyTab and states[tab]:
            print eval(tab)('grey')
        elif states[tab]:
            print eval(tab)('blue')

def linksLine():
    if states == {}: initStates()
    for tab in tabs:
        if states[tab]:
            print links[tab]
    print '     <a href="http://www.weatheroffice.ec.gc.ca">WXO</a>'

def printMainImage():
    print '            <td><img src="/images/head4.jpg" border="0" vspace="0" hspace="0" \
           alt="Class Object Library Used to Merge and Broadcast Observations" align="right" valign="bottom" height="40" width="444"></td>'

def printMainImageCenter():
    print '            <img src="/images/head4.jpg" border="0" vspace="0" hspace="0" \
           alt="Class Object Library Used to Merge and Broadcast Observations" align="center" valign="top" height="40" width="444">'

if __name__ == '__main__':

    #tabsLine()
    tabsLine('pdsSources')
    print
    linksLine()

