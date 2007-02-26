"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#####################################################################
# Name: errorLog.py
#
# Author: Dominik Douville-Belanger
# 
# Date: 2005-03-31
#
# Description: Functions and utilities to log error situations 
#
#####################################################################

from PXPaths import *
from ColumboPath import *
from Logger import Logger
from ConfigParser import ConfigParser
import sys
import readMaxFile
import CompositeNCSCircuit
import errorLog
import re
import time

class EmptyFileError(Exception): pass

def logPx(logger, logname, wamsLog, name, type, lastRcv, lastTrans, totalQueue, socket, bestLog, statusCCT, statusLog, limitQueue, statusSocket, statusRx, statusTx):
    """
    Use the info parsed for the website to detect any errors for NCS/px.
    """
    print name
    # Circuit Error
    if statusCCT != 0:
        if statusCCT == 1:
            logger.warning("%s: circuit is down on at least one machine" % (name))
            wamsLog.write("[WARNING] %s: circuit is down on at least one machine\n" % (name))
        elif statusCCT == 2:
            logger.error("%s: circuit is down on all backend" % (name))
            wamsLog.write("[ERROR] %s: circuit is down on all backend\n" % (name))
        else:
            logger.critical("%s: invalid circuit status code found -> %d" % (name, statusCCT))
    
    # Socket Error
    if statusSocket != 0:
        if statusSocket == 1:
            message = "%s: there is a network socket but it is presently not established" % (name)
            logger.warning(message)
            # Special check for the wams log
            if checkOccurences(logname, 'WARNING', message, 3, 240): # 3 times over 180 seconds (60 secs being one crontab run)
                wamsLog.write("[WARNING] %s\n" % (message))
        elif statusSocket == 2:
            message = "%s: socket is down" % (name)
            logger.error(message)
            # Special check for the wams log
            if checkOccurences(logname, 'ERROR', message, 2, 180):
                wamsLog.write("[ERROR] %s\n" % (message))
        else:
            logger.critical("%s: invalid socket status code found -> %d" % (name, statusSocket))
    
    # Best log line Error
    if statusLog == 1:
        logger.error("%s: log shows this error -> %s" % (name, bestLog))
        wamsLog.write("[ERROR] %s: log shows this error -> %s\n" % (name, bestLog))
    elif statusLog != 0:
        logger.critical("%s: invalid log status code found -> %d" % (name, statusLog))
    
    # Queue too high
    if totalQueue > limitQueue:
        logger.error("%s: queue is too high (%d when limit is %d)" % (name, totalQueue, limitQueue))
        wamsLog.write("[ERROR] %s: queue is too high (%d when limit is %d)\n" % (name, totalQueue, limitQueue))
    
    # Last reception outdated
    if statusRx == 1:
        logger.error("%s: last reception is outdated -> %s" % (name, lastRcv))
        wamsLog.write("[ERROR] %s: last reception is outdated -> %s\n" % (name, lastRcv))
    elif statusRx != 0:
        logger.critical("%s: invalid last reception status code found -> %d" % (name, statusRx))
    
    # Last transmission outdated
    if statusTx == 1:
        logger.error("%s: last transmission is outdated -> %s" % (name, lastTrans))
        wamsLog.write("[ERROR] %s: last transmission is outdated -> %s\n" % (name, lastTrans))
    elif statusTx != 0:
        logger.critical("%s: invalid last transmission status code found -> %d" % (name, statusTx))

# Coming soon...
def logPDS():
    pass

def checkOccurences(logname, level, message, ammount, delay):
    """
    We verify if a message appears a certain ammount of time over given
    period in a log file.
    Parameters:
        logname -> the log top scan
        level   -> the message log level (e.g. WARNING)
        message -> the message to scan for
        ammount -> number of times it has to occur in a row
        delay   -> the time range in seconds in which the consecutive log entries must be
    Returns: True (1) or False (0)
    """

    currentTime = time.mktime(time.localtime())
    # Regular expression model: 2005-07-05 13:38:02,258 [WARNING] ukmet: blah blah blah
    regex = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \[%s\] %s" % (level, message))
    loglines = open(logname, 'r').readlines()
    loglines.reverse()
    loglines = '\n'.join(loglines)
    itemIter = regex.finditer(loglines)
    nextTime = currentTime
    while 1:
        try:
            match = itemIter.next()
            timestamp = time.mktime(time.strptime(match.group(1), "%Y-%m-%d %H:%M:%S"))
            if timestamp + delay >= currentTime:
                ammount -= 1
                if ammount == 0:
                    return 1
            else:
                return 0
        except StopIteration:
            return 0

############################################################################
# Utility functions                                                        #
# When they start being used by the webserver, some functions will have to #
# move... again.                                                           #
############################################################################
def getNCSMax(circuitDict):
    theCircuits = circuitDict.keys()
    circuitRegex, defaultCircuit, timerRegex, defaultTimer, DUMMY, DUMMY = readMaxFile.readQueueMax(FULL_MAX_CONF, "PX")
    circuitMax = readMaxFile.setValueMax(theCircuits, circuitRegex, defaultCircuit)
    timerMax = readMaxFile.setValueMax(theCircuits, timerRegex, defaultTimer)
    return circuitMax, timerMax

def isInError (clientDict, name):
    myClient = clientDict[name]
    machines = clientDict[name].getHosts()
    #regex = re.compile(r'ERROR|has been queued too long|Timeout|\[ERROR\]')
    regex1 = re.compile(r'ERROR|has been queued too long|Timeout|\[ERROR\]')
    regex2 = re.compile(r"Interrupted system call|425 Can't build data connection")
    """
    for machine in machines:
        match = regex.search(myClient.getLastLog(machine)[0])
        if (match):
            return 1
    return 0
    """
    if regex1.search(myClient.getBestLog()):
        if regex2.search(myClient.getBestLog()):
            return 0
        else:
            return 1
    return 0
    
def tooLong(lastCom, limit):
    if lastCom == "NOT FOUND":
        return 1
    nbSec = limit * 60
    now = time.localtime()
    last = time.strptime(lastCom, "%Y-%m-%d %H:%M:%S")
    if time.mktime(now) - nbSec > time.mktime(last):
        return 1
    else:
        return 0

def errorCheck(logger, logname, wamsLog, circuitDict):
    config = ConfigParser()
    config.readfp(open(FULL_MAIN_CONF))
    keys = circuitDict.keys()
    circuitMax, timerMax = getNCSMax(circuitDict) 
    for key in keys:
        circuit = circuitDict[key]
        stopped = circuit.getGlobalStatus() # 1 if stopped partially, 2 if completely stopped, 0 if OK
        inError = isInError(circuitDict, key) # 1 if in error
        if circuit.getGlobalType().find('pxReceiver') != -1:
            rcv = tooLong(circuit.getGlobalLastRcv(), int(timerMax[key]))
            trans = 0
        elif circuit.getGlobalType().find('pxSender') != -1:
            trans = tooLong(circuit.getGlobalLastTrans(), int(timerMax[key]))
            rcv = 0
        # We want a master log of all errors that ever happened.
        logPx(logger, logname, wamsLog, key, circuit.getGlobalType(), circuit.getGlobalLastRcv(), circuit.getGlobalLastTrans(), circuit.getCompositeQueue(), circuit.getSocketState(), circuit.getBestLog().rstrip("\n").replace('"', "'"), stopped, inError, int(circuitMax[key]), circuit.getSocketFlag(), rcv, trans)
