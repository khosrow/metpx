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
import CollectionBuilder
import CollectionConfigParser
import time

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

        #-----------------------------------------------------------------------------------------
        # Creating CollectionBuilder object to give us access to CollectionBuilder methods
        #-----------------------------------------------------------------------------------------
        self.collectionBuilder = CollectionBuilder.CollectionBuilder(self.logger) 

        #-----------------------------------------------------------------------------------------
        # Creating CollectionConfig object to give us access and control over collection 
        # config parameters
        #-----------------------------------------------------------------------------------------
        self.collectionConfig = CollectionConfigParser.CollectionConfigParser(self.logger,self.source)


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
      
        #-----------------------------------------------------------------------------------------
        # use collectionBuilder to create a bulletin object from the given file
        #-----------------------------------------------------------------------------------------
        bulletin = self.collectionBuilder.buildBulletinFromFile(fileName)

        #-----------------------------------------------------------------------------------------
        # Let's find out if the report arrived on time
        #-----------------------------------------------------------------------------------------
        if (self.isReportOnTime(bulletin)):
            self.logger.info("COMPLETEME: The report was on time")
        else:
            self.logger.info("COMPLETEME: The report was NOT on time")

        #-----------------------------------------------------------------------------------------
        # REMOVEME
        #-----------------------------------------------------------------------------------------
        #self.logger.info("Source.type in collector is: %s" % self.source.type)
        #self.logger.info("The new bulletin's Header is: %s" % bulletin.getHeader())
        #self.logger.info("The new bulletin's time is: %s" % bulletin.getTimeStamp())

        #-----------------------------------------------------------------------------------------
        # COMPLETEME
        #-----------------------------------------------------------------------------------------
        return 'THIS IS A FAKE RETURN IN CollectionManager.py'


    def isReportOnTime(self, bulletin):
        """ isReportOnTime(bulletin) -> Boolean

            Given the bulletin, returns True if the bulletin is considered on time
            and an empty string if the bulletin is not considered on time.
        """
        presentTime = time.strftime("%d%H%M",time.localtime())
        bulletinTime = bulletin.getTimeStamp()

        self.logger.info("COMPLETEME presentTime is: %s" % presentTime)
        self.logger.info("COMPLETEME bulletin time is: %s" % bulletinTime)

if __name__ == '__main__':
    pass
