"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
###########################################################
# Name: NCSUtils.py
#
# Author: Dominik Douville-Belanger
# 
# Date: 2005-01-21
#
# Description: Various utility functions and tests
#              not supported directly by the 
#              ColumboCrimeScene since NCS verifications 
#              need to support more tests.
#
###########################################################
"""

import commands, time, socket, re

def configParse(file):
    """
    This function parses a config file for specific data fields.
    Returns a tuple of 2 elements:
        - The circuit type (default: '')
        - The socket port (default: 0)
    """

    type = ''
    port = 0
    configFile = open(file, 'r')
    lines = configFile.readlines()
    for line in lines:
        match = re.compile(r"^\s*(\S+)\s* \s*(\S+)\s*$").search(line)
        if match:
            field, value = match.group(1,2)
            if field == 'type':
                type = value.strip("'").upper()
            if field == 'port' or 'portS':
                port = value
            if field == 'destination':
                if value.find('ftp://') == -1:
                    port = value.split(':')[-1]
                else:
                    port = 0
    configFile.close()
    return type, port

def socketInfo(port, dir, nsInfo):
    """
    Parses the results of the 'netstat -an' command to find the state of a socket connection.
    Returns a string giving details about the socket's state.
    """

    port = str(port)
    # Two nasty regexes. They perfectly match the result lines of netstat -an
    localRegex = re.compile(r"^\S+\s+\d+\s+\d+\s+\d+\.\d+\.\d+\.\d+:" + port + r"\s+\d+\.\d+\.\d+\.\d+:\S+\s+(\S+)\s*$")
    remoteRegex = re.compile(r"^\S+\s+\d+\s+\d+\s+\d+\.\d+\.\d+\.\d+:\S+\s+\d+\.\d+\.\d+\.\d+:" + port + r"\s+(\S+)\s*$")
    regex = ''
    if dir == 'pxReceiver':
        regex = localRegex
    elif dir in ['pxSender', 'pxTransceiver']:
        regex = remoteRegex
    
    info = ''
    for line in nsInfo:
        match = regex.search(line)
        if match:
            if match.group(1) == 'ESTABLISHED':
                return 'ESTABLISHED' + ' ' + socket.gethostname() + ': ' + str(port)
            else:
                info = match.group(1) + ' ' + socket.gethostname() + ': ' + str(port)
    if info == '':
        return 'DOWN' + ' ' + socket.gethostname() + ': ' + port
    return info

def lastFullLine(lines):
    """
    Pretty straightforward. Gets the last non-empty line of a file.
    """
    candidate = ''
    for line in lines:
        for char in line:
            if char not in '\n\t ':
                candidate = line
                break
    if candidate == '':
        raise EmptyFileError
    return candidate

def lastSendRcv(logname, regex):
    """
    Gives the time of the last reception or transmission (or technically anything else) that was logged in
    the available log files.
    Parameters: - The log name
                - The regular expression we want to match
    Returns the struct_time tuple containaing the time of the event (default: UNIX 0 hour)
    """
    EPOCH = time.gmtime(0)
    dir = commands.getoutput('ls ' + logname + '*').split()
    logs = []
    for d in dir:
        if d.find('debug') == -1: # We do not want the debug logs
            logs.append(d)
    if len(logs) == 0:
        return EPOCH # Default value
    logs.sort(); logs.reverse()
    # The logs are sorted alphanumerically, thus the current log (the one with no date extension)
    # is currently at the tail of the list. So we need to swap it with the head of the list
    # Sort of a one-shot inline function. Swaps the first and last entry
    tmp = []; tmp.append(logs[-1]); tmp.extend(logs); del tmp[-1]; logs = tmp
    for log in logs:
        lasttime = commands.getoutput('egrep ' + '"' + regex + '"' + ' ' + log + ' | tail -1').split()
        if len(lasttime) > 0:
            try:
                return time.strptime(lasttime[0] + ' ' + lasttime[1][:-4], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return EPOCH
    return EPOCH # Default value

def queueLength(path):
    total = 0
    for i in range(1,6): # In case there are some weird directories beside priority 1 to 5
        status, items = commands.getstatusoutput('ls -1FR ' + path + '/' + str(i)) # -F option is used to determine file type
        items = items.splitlines()
        if status == 0:
            for item in items:
                if len(item) > 0 and item[-1] not in ['/', ':']:
                    total += 1
    return total

if __name__ == '__main__':

    print lastSendRcv('/apps/px/log/tx_wmoTx.log', r"\[INFO\].* livr")
