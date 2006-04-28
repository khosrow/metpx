#!/usr/bin/env python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

##############################################################
# Name: SearchUtils.py
#
# Author: Dominik Douville-Belanger
#
# Description: Various utility functions for the bulletins
#              search and send feature of columbo px
#
# Date: ???
#
##############################################################

import os
import re
import commands
import time
import pickle
from ConfigParser import ConfigParser
from PDSPath import *
from ColumboPath import *

import HeaderInfo
from CompositeNCSCircuit import CompositeNCSCircuit

config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))
header2client = config.get('RESEND', 'header2client') # Path to the header2client file
backends = config.get('CIR', 'backends').split(' ')   # Which machines are part of the backend cluster
frontend = config.get('CIR', 'frontend').split(' ')

# Regex for senders with a byte count. Header isn't preceded by the DB path.
TXBYTERGX = re.compile(r"(\d+):(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[\S+\] \(.*\) \S+ ([^\s/]+)")
# Regex used for the tx_coll circuit. Header isn't preceded by the DB path.
TXCOLLRGX = re.compile(r"(\d+):(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[\S+\] fichier ([^\s/]+)")
# Regex the general senders. Header is preceded by the DB path.
TXGENRGX = re.compile(r"(\d+):(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[\S+\] Bulletin (\S+/)([^\s/]+)")
# Regex used with ingester receivers. Header is preceded by the DB path.
RXINGESTRGX = re.compile(r"(\d+):(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[\S+\] ingest (\S+/)([^\s/]+)")
# Regex used to get ingested bulletins destination. The result beging a space separated string.
RXQUEUEDRGX = re.compile(r"(\d+):(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[\S+\] queued for (.+)")
# Regex used with bulletins that have been unlinked.
UNLINKEDRGX = re.compile(r"(\d+):(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[\S+\] No pattern matching: \S+/([^\s/]+)")

# This dictionary contains uses the name of the regex as a key and the element is the actual regex and its number of internal group
rgxdict = {'txbytergx' : (TXBYTERGX, 3), 'txcollrgx' : (TXCOLLRGX, 3), 'txgenrgx' : (TXGENRGX, 4), 'rxingestrgx' : (RXINGESTRGX, 4), 'rxqueuedrgx' : (RXQUEUEDRGX, 3), 'unlinkedrgx' : (UNLINKEDRGX, 3)}

def unarchiveResults(filename):
    """
    Unpickle the result file 
    Arguments:
        filename -> the pickle.dump file
    Returns: a dictionnaru of CompositeNCSCircuit objects
    """
    
    file = open(filename, "rb")
    compositeCircuitDict = pickle.load(file)
    file.close()
    return compositeCircuitDict

def wildCardCheck(str):
    """
    Transform standard wild cards into egrep groups
    Arguments:
        str -> the string which contains the wildcards to transform
    Returns: a string
    """
    
    try:
        int(str)
    except ValueError:
        return str.replace('*', r'[[:alnum:]-]+')
    return str.replace('*',r'[[:digit:]]+')

def filterTime(logtime, logbegin, logend):
    """
    If timestamp is within acceptable boundaries
    Arguments:
        logtime  -> timestamp found in the log
        logbegin -> lower limit
        logend   -> upper limit
    Returns: 0 or 1
    """
    
    if logbegin == 0 and logend == 0: # If both boundaries are not set
        return 1
    elif logbegin == 0 and logtime <= logend: # If no start time is specified
        return 1
    elif logend == 0 and logtime >= logbegin: # If no end time is specified
        return 1
    elif logtime >= logbegin and logtime <= logend: # If both are specified
        return 1
    else:
        return 0

def searchLog(logPath, hosts, direction, request, logbegin, logend):
    """
    Search in the log for the request created through BulletinResender.py web interface
    Splits the results into usefull parts and creates HeaderInfo objects.
    Arguments:
        logPath   -> path to the log
        side      -> backend or frontend machine
        direction -> is it a sender or a receiver
        request   -> the egrep regular expression request
        logbegin  -> beginning date
        logend    -> end date
    Returns: a list of HeaderInfo objects
    """

    headerList = []
    for host in hosts:
        results = []
        command = """sudo -u pds /usr/bin/ssh %s 'egrep -n "%s" %s'""" % (host, request, logPath) # The search
        status, output = commands.getstatusoutput(command)
        results += dismemberResult(output) # Gets a list of of each matches group
        for result in results:
            machine = host
            # Assign the groups we need
            linenumber = result[0]
            if len(result) == 3:
                dbpath = ''
                header = result[2]
            else:
                dbpath = result[2]
                header = result[3]
            queuedFor = []
            
            # Check if the result is in our time boundaries
            logtime = time.strptime(header.split(':')[-1].strip(' '), '%Y%m%d%H%M%S')
            # We reset the minutes and seconds
            logtime = list(logtime)
            logtime[4] = logtime[5] = 0
            logtime = tuple(logtime)
            
            if filterTime(time.mktime(logtime), time.mktime(logbegin), time.mktime(logend)):
                headerList.append(HeaderInfo.HeaderInfo(machine, direction, logPath, linenumber, logtime, header, queuedFor, dbpath))

    return headerList

def dismemberResult(rawResult):
    """
    Takes the output of the massive grep and cuts it into bits and bites
    Returns a list of line parts which are represented as list themselves
    e.g.: [['hi','there'], ['blue','sky']]
    Arguments:
        rawResult -> a long string return by egrep
    Returns: a list fo lists
    """
    
    # Defaults
    validRegex = None
    dismemberedLines = []
    
    # This is the first pass to find which type of regex fits
    for key in rgxdict.keys():
        if rgxdict[key][0].search(rawResult) != None:
            validRegex = rgxdict[key][0]
            groupCount = rgxdict[key][1]
            break
    if validRegex == None:
        return [] # Defaults to an empty list
        
    partIter = validRegex.finditer(rawResult) # Extract each matching line
    while 1:
        try:
            match = partIter.next()
            dismemberedLines.append([match.group(i) for i in range(1, groupCount + 1)]) # Grab each parts and append to the list
        except StopIteration:
            break
    return dismemberedLines

def accessDB(header):
    """
    Form a database path from a bulletin's header.
    Arguments:
        header -> the header
    Returns: a path string
    """
    
    ttaaii, ccccxx, src, headertime = splitHeader(header)
    dbPath = '/apps/px/db/%s/%s/%s/%s/%s' % (headertime, ttaaii[0:2], src, ccccxx, header)
    return dbPath

def readFromDB(host, dbPath):
    """
    Reads a bulletin file from the database.
    The output is copied to a temporary file on the local machine.
    Arguments:
        host   -> machine that hosts the bulletin file
        dbPath -> path to the bulletin in the database
    Returns: path to the bulletin's copy
    """
    
    status, output = commands.getstatusoutput("sudo -u pds /usr/bin/ssh %s cat %s" % (host, dbPath))
    if not status:
        return output.replace('\n', '<br>')
    else:
        return ''

def splitHeader(header):
    """
    Extracts some useful fields from a bulletin's header.
    These fields are the TTAAii, the CCCCxx, the SRC and the headertime at the header's end
    Arguments:
        header -> the header
    Returns: a four-tuple 
    """
    
    pxHeaderParts = header.split('_')
    pdsHeaderParts = header.split(':')
    ttaaii = pxHeaderParts[0]
    ccccxx = pxHeaderParts[1]
    src = pdsHeaderParts[1]
    headertime = pdsHeaderParts[-1].strip(' ')[0:8] # Shortens the date display

    return ttaaii, ccccxx, src, headertime

def possibleDestination(header, host):
    """
    Returns a list of where you can send a bulletin.
    Arguments:
        header -> the header
        host   -> on which host
    Returns: a list of string
    """
    
    ncsResults_name = config.get('CIR', 'px_results_name')
    if host in frontend:
        ncsResults_name += '_local'
    circuitDict = unarchiveResults("/apps/pds/tools/Columbo/ColumboShow/results/" + ncsResults_name)
    
    ttaaii, ccccxx, src, headertime = splitHeader(header)
    command = """sudo -u pds /usr/bin/ssh %s 'egrep -m 1 "^%s %s:" %s'""" % (host, ttaaii, ccccxx, header2client)
    status, output = commands.getstatusoutput(command)
    if not status:
        parts = output.strip().split(':')
        destinations = parts[1].split()
        return [d for d in destinations if d in circuitDict.keys() and circuitDict[d].getType(host).lower().find('pxreceiver') == -1]
    else:
        return []

def possibleLog(host, dir):
    """
    Returns a list of logs that can be searched.
    In order to be searchable, the corresponding circuit must be
    active and their type must be 'am', 'wmo', 'bulletin-file' or 'amis'.
    Arguments:
        host -> machine which contains the logs
        dir  -> type of log rx or tx
    Returns: a list of string
    """

    ncsResults_name = config.get('CIR', 'px_results_name')
    # DL if host == os.uname()[1]:
    if host in frontend:
        ncsResults_name += '_local'
    circuitDict = unarchiveResults("/apps/pds/tools/Columbo/ColumboShow/results/" + ncsResults_name)

    valid = []
    for key in circuitDict.keys():
        type = circuitDict[key].getType(host).lower()
        if dir == 'rx' and type.find('pxreceiver') != -1:
            if type.find('am') != -1 or type.find('wmo') != -1 or type.find('bulletin-file') != -1 or type.find('amis') != -1:
                valid.append(key)
        elif dir == 'tx' and type.find('pxsender') != -1:
            if type.find('am') != -1 or type.find('wmo') != -1 or type.find('bulletin-file') != -1 or type.find('amis') != -1:
                valid.append(key)
    return valid
