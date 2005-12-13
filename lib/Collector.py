"""
#############################################################################################
# Name: Collector.py
#
# Author: 
#
# Date: 2005-12-13
#
# Description:
#
#############################################################################################

"""
import sys, os, os.path, time, string, commands, re, signal, fnmatch
sys.path.insert(1,sys.path[0] + '/../lib/importedLibs')

import PXPaths
from Logger import Logger

PXPaths.normalPaths()              # Access to PX paths

class Collector(object):

    def __init__(self, logger=None):
        self.logger = logger

    def collect(self, filename):
        self.logger.info("Collector.collect() has been called")
        file = open(filename, 'r')
        rawBull = file.read()
        self.logger.info("%s" % rawBull)
        return rawBull

if __name__ == '__main__':
    pass
