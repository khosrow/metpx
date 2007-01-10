"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

###########################################################
# Name: MsgOpUtils.py
#
# Author: Dominik Douville-Belanger
#
# Date: 2005-04-04
#
# Description: Various utilities for MSGOP
#
###########################################################

from PDSPath import *
from ColumboPath import *
from ConfigParser import ConfigParser

import commands
import time
import os

config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
msgPath = config.get('OPERATOR', 'msg_path')
backends = config.get('CIR', 'backends').strip(' ').split(' ')
frontend = config.get('CIR', 'frontend').split(' ')

def getMsg():
    """
    Gets available messages from the machines.
    Returns: a list of strings
    """
    
    machines = backends[:] + frontend[:]
    uniqueMachines = {}
    for machine in machines: uniqueMachines[machine] = 1 
    machines = uniqueMachines.keys()

    result = []
    for machine in machines:
        status, items = commands.getstatusoutput('sudo -u pds /usr/bin/ssh ' + machine + ' ls -1F ' + msgPath)
        if status == 0:
            items = items.splitlines()
            for item in items: # Cleans up the list (in case there are some directory)
                if len(item) > 0 and item[-1] not in [':', '/']:
                    result.append((item, machine))
    return result

def acknowledgeMsg(msgName, machine):
    """
    Appends '.ack' to a file name.
    Arguments:
        msgName -> name of the message to modify
        machine -> on which host
    Returns: the status and output of the 'mv' command
    """
    
    if msgName.find('.ack') == -1:
        msgName = msgPath + '/' + msgName
        ackName = msgName + '.ack'
        status, result = commands.getstatusoutput('sudo -u pds /usr/bin/ssh ' + machine + ' mv ' + msgName + ' ' + ackName)
        return status, result
    else:
        return 0, ''

def removeMsg(msgName, machine):
    """
    Deletes a message on a distant host
    Arguments:
        msgName -> name of the message to modify
        machine -> on which host
    Returns: the status and output of the 'mv' command
    """
    
    msgName = msgPath + '/' + msgName
    status, result = commands.getstatusoutput('sudo -u pds /usr/bin/ssh ' + machine + ' rm ' + msgName)
    return status, result

def msgToHTML(msgName, machine):
    """
    Format a message's content into proper HTML.
    Arguments:
        msgName -> name of the message to modify
        machine -> on which host
    Returns: the status and output of the 'mv' command
    """
    
    completePath = msgPath + '/' + msgName
    status, output = commands.getstatusoutput('sudo -u pds /usr/bin/ssh %s cat %s' % (machine, completePath))
    if not status:
        return output.replace('\n', '<br>')
    else:
        return ''
