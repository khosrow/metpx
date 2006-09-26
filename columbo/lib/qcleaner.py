#!/usr/bin/python2
#!/software/pub/python-2.3.3/bin/python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

############################################################################
# Name: qcleaner.py
#
# Author: Dominik Douville-Belanger
#
# Description: A utility program which resides on the backends and provides
#              a secure way of delete files in queue.
#              It can be used through the web interface available in each
#              px enabled Columbo or by command line.
#
# Date: 2005-05-24
#
############################################################################

import sys
import commands
import getopt
import time
import os

from PDSPath import *

class EmptyList(Exception): pass

def verifyPath(path):
    """
    I think this method code is pretty self-explanatory.
    It verifies the path to be sure the user is not doing something
    naughty.
    path -> the path to verify
    """
    if path.find('..') != -1:
        print 'Deleting in an higher directory was attempted. Exiting...'
        sys.exit(2)
    if path.find('/apps/px/txq/') != 0 and path.find('/apps/px/rxq/') != 0:
        print 'Trying to delete outside of /apps/px/<queues>. Exiting...'
        sys.exit(2)

def listToString(path, lst):
    """
    Transform a list of words in a string of space separated words.
    Each word as a common path prepended to it.
    This function also call verifyPath() on each complete words.
    path -> is the base path you want to prepend to all the words
    lst -> the list of words
    """
    result = ''
    if len(lst) == 0:
        raise EmptyList
    for l in lst:
        str = path + '/' + l
        verifyPath(str) # We must be sure no one entered a file name like '../../something'
        result += (str + ' ')
    return result

def deletePriority(basePath, name, toDelete):
    """
    Deletes an entire priority (e.g. /apps/px/txq/amis/1)
    This means all hour directory inside it will be purged,
    except for the current hour directory.
    basePath -> the basic path to the circuit (e.g. /apps/px/txq) NO ENDING '/'
    name -> the circuit name
    toDelete -> the list of priorities to delete (e.g. [1,3,4])
    """
    path = basePath + '/' + name
    for td in toDelete:
        hourDirs = os.listdir(path + '/' + td)
        if len(hourDirs) == 0:
            print 'Nothing to delete'
            sys.exit(0)
        # In order to spare the current hour directory in each priority
        # we must delete each priority's content individually.
        deleteHour(basePath, name, td, hourDirs)
    
def deleteHour(basePath, name, priority, toDelete):
    """
    Deletes an hour directory.
    If the directory is the current one, it only cleans its content.
    basePath -> the basic path to the circuit (e.g. /apps/px/txq) NO ENDING '/'
    name -> the circuit name
    priority -> under which priority are you working
    toDelete -> a list of date-hour like [2005051522, 2005051712] to delete
    """
    path = basePath + '/' + name + '/' + priority
    batchJob = []
    for td in toDelete:
        currentTime = time.strftime('%Y%m%d%H', time.localtime()) # Gets the current time
        if currentTime == td:
            verifyPath(path + '/' + td) # An explicit call just for this case
            command = "find %s -name '*' -print0 -type 'f' | xargs -0 rm -f" % (path + "/" + td + "/")
            print 'Special case: ' + command # <-------- DEBUG
            status, output = commands.getstatusoutput(command)
        else:
            batchJob.append(td)
    if len(batchJob) > 0:
        hours = listToString(path, batchJob)
        command = 'rm -rf ' + hours
        print command # <----------------------------------- DEBUG
        status, output = commands.getstatusoutput(command)
    
def deleteFile(basePath, name, priority, hour, toDelete):
    """
    basePath -> the basic path to the circuit (e.g. /apps/px/txq) NO ENDING '/'
    name -> the circuit name
    priority -> under which priority are you working
    hour -> in which hour are you working
    toDelete -> a list of complete bulletin filename to delete
    """
    path = basePath + '/' + name + '/' + priority + '/' + hour
    files = listToString(path, toDelete) # A call to listToString also verifies the path
    command = 'rm -f ' + files
    print command # <----------------------------------- DEBUG
    status, output = commands.getstatusoutput(command)
    
def usage():
    print 'Usage: ./qcleaner.py [-p=priority] [-h=hour] --type=type --name=circuitname <list_of_things_to_delete>'
    print '\t-p Specifies you want to delete in this priority level'
    print '\t-h Specifies you want to delete for this precise hour'
    print '\t--type Reception (rx) or transmission (tx)'
    print '\t--name Name of the circuit to clean'
    print '\tDo not specify either -p or -h if you want to delete complete priorities.'
    print ''
    print 'Examples:'
    print '\tTo delete the content of priorities 3, 4 and 5: qcleaner.py --type tx --name amis 3 4 5'
    print '\tTo delete the content of a precise hour in priority 2: qcleaner.py --type tx --name amis -p 2 2005052413'
    print '\tTo delete certain bulletins in priority 1 at 2005051816: qcleaner.py --type tx --name amis -p 1 -h 2005051816 WSAG_SAME_181600_05140:nws-alph:SAME:WS:2:Direct:20050518160845'
    
def main():
    if len(sys.argv) <= 3: # Not enough arguments
        usage()
        sys.exit(2)
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'p:h:', ['type=', 'name='])
    except getopt.GetoptError: # Unrecognizable arguments
        # print help information and exit
        usage()
        sys.exit(2)
    name = ''
    cctType = ''
    priority = ''
    hour = ''
    toDelete = args
    try:
        for opt, arg in opts:
            if opt == '-p':
                priority = str(arg)
            elif opt == '-h':
                hour = str(arg)
            elif opt == '--name':
                name = arg
            elif opt == '--type':
                cctType = arg
    except ValueError: # Option missing argument
        print 'Invalid options.\n'
        usage()
        sys.exit(2)

    if name == '' or cctType == '' or toDelete == []:
        print 'The program is missing necessary arguments.\n'
        usage()
        sys.exit(2)
        
    if cctType == 'tx':
        basePath = TXQ
    elif cctType == 'rx':
        basePath = RXQ
    else:
        print 'Some arguments you entered seem invalid.\n'
        usage()
        sys.exit(2)
    
    removeType = ''
    if priority != '' and hour != '':
        deleteFile(basePath, name, priority, hour, toDelete)
    elif priority != '':
        deleteHour(basePath, name, priority, toDelete)
    else:
        deletePriority(basePath, name, toDelete)
    
if __name__ == "__main__":
    main()
