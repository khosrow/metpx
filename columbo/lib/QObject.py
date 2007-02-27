"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

##################################################################
# Name: q_object.py
#
# Author: Dominik Douville-Belanger
#
# Date: 2005-03-10
#
# Description: Object that holds the list of machines and computes
#              queues. Was design as an object because at the
#              beginning it also contained the values of the
#              computations.
#
##################################################################

import cgi
import cgitb; cgitb.enable()

import sys, commands, pickle, re, os
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib");
from PXPaths import *
from ColumboPaths import *

from ConfigParser import ConfigParser
config = ConfigParser()
config.readfp(open(FULL_MAIN_CONF))

class QObject:

    def __init__(self, host):
        if host == "backends":
            self.machines = config.get('CIR', 'backends').split(' ')
        elif host == "frontend":
            self.machines = config.get('CIR', 'frontend').split(' ')
            
########################################################################
# The following methods all do a similar job but are different enough
# to justify the use of multiple functions.
########################################################################
    def census(self, path):
        """
        All files (not directory) under path. Used to get maximum details on which files are in queue.
        """
        result = []
        for machine in self.machines:
            files = []
            if  machine != os.uname()[1]:
                status, tmp = commands.getstatusoutput('sudo -u pds /usr/bin/ssh ' + machine + ' ls -1FR ' + path)
            else:
                status, tmp = commands.getstatusoutput('ls -1FR ' + path)
            tmp = tmp.split('\n')
            
            if status != 0 or len(tmp) == 0:
                continue
            for t in tmp:
                if len(t) > 0 and t[-1] not in [':', '/']:
                    files.append(t)
            if len(files) == 0:
                continue
            
            for file in files:
                result.append((file, machine))
        return result
    
    def timedir(self, path):
        """
        Retreives the name of time directory found in a priority directory.
        """
        result = []
        for machine in self.machines:
            if machine != os.uname()[1]:
                status, items = commands.getstatusoutput('sudo -u pds /usr/bin/ssh ' + machine + ' ls -1F ' + path)
            else:
                status, items = commands.getstatusoutput('ls -1F ' + path)
            items = items.splitlines()
            if status == 0:
                for item in items:
                    if len(item) > 0 and item[-1] == '/' and item[:-1] not in result:
                        result.append(item[:-1])
        return result
    
    def count(self, path):
        """
        Counts all files in a given path. Used to get number of files in a priority directory
        """
        total = 0
        for machine in self.machines:
            status, items = commands.getstatusoutput('sudo -u pds /usr/bin/ssh ' + machine + ' ls -1FR --ignore=PROBLEM ' + path)
            items = items.splitlines()
            if status == 0:
                for item in items:
                    if len(item) > 0 and item[-1] not in ['/', ':']:
                        total += 1
        return total
