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
        self.logger = logger   # Logger object

    def collect(self, filename):
        """
        Read the content of filename and determine what to do. If the bulletin must be sent
        immediately, return the bulletin (as a string). If it must be retained for later treatment,
        return an empty string.
        """
        self.logger.info("Collector.collect() has been called")
        file = open(filename, 'r')
        rawBull = file.read()
        self.logger.info("%s" % rawBull)
        return rawBull

if __name__ == '__main__':
    pass
