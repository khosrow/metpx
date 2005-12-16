"""
#############################################################################################
# Name: CollectionManager.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           Travis Tiegs (National Software Development<nssib@ec.gc.ca>)
#
# Date: 2005-12-02
#
# Description:  This module gives us the ability to file reports and send out immediate
#               collections if necessary. Scheduled collections are not handled by this 
#               module.
#
# Revision History: 
#               2005-12-13 Daniel Lemay provided function stub
#############################################################################################
"""
__version__ = '1.0'

import sys, os, os.path, time, string, commands, re, signal, fnmatch
sys.path.insert(1,sys.path[0] + '/../lib/importedLibs')

import PXPaths
from Logger import Logger

PXPaths.normalPaths()              # Access to PX paths

class CollectionManager(object):
    """The CollectionManager class

           Files incoming reports, and sends out immediate collections
           if necessary.

           Author:      National Software Development<nssib@ec.gc.ca>
           Date:        December 2005
    """
    def __init__(self, source, logger=None):
        self.source = source   # Source object containing configuration infos about the collector
        self.logger = logger   # Logger object

    def collectReport(self, fileName):
        """ collectReports (self, fileName)

            Read the content of filename and determine if the bulletin needs to be 
            sent immediately, or if it can be sent at the end of the collection
            interval.

            Return values:
                rawBulletin: Text string -  returning the bulletin so that it can be sent
                                            immediately.

                EmptyString: Empty Text sring - Indicating that the bulleting does not
                                                need to be sent immediately.
        """
        self.logger.info("collectReports() has been called")
        file = open(fileName, 'r')
        rawBulletin = file.read()
        self.logger.info("** In collector, the bulletin reads: %s" % rawBulletin)
        self.logger.info("Source.type in collector is: %s" % self.source.type)
        return rawBulletin

if __name__ == '__main__':
    pass
