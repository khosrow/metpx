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

import datetime 
import PXPaths
from Logger import Logger
import CollectionBuilder
import CollectionConfigParser
import time
import BulletinCollection
import BulletinWriter

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

        #-----------------------------------------------------------------------------------------
        # A placeholder for the bulletin object that will be set for this class to use
        #-----------------------------------------------------------------------------------------
        self.bulletin = ''

        #-----------------------------------------------------------------------------------------
        # A BulletinWriter object to carry out disk-related tasks
        #-----------------------------------------------------------------------------------------
        self.bulletinWriter = BulletinWriter.BulletinWriter(self.logger,self.collectionConfig)


    def collectReport(self, fileName):
        """ collectReports (self, fileName)

            Read the content of filename and determine if the bulletin needs to be 
            sent immediately, or if it can be sent at the end of the collection
            interval. This method contains all of the business logic neede to 
            determine if a bulletin needs to be collected.  For more information
            about the business logic and the flow of this method, please see the 
            "Collection Process Flow diagram" document.

            Return values:
                rawBulletin: Text string -  returning the bulletin so that it can be sent
                                            immediately.

                EmptyString: Empty Text sring - Indicating that the bulleting does not
                                                need to be sent immediately.
        """
        #-----------------------------------------------------------------------------------------
        # use collectionBuilder to create a bulletin object from the given file
        #-----------------------------------------------------------------------------------------
        self.bulletin = self.collectionBuilder.buildBulletinFromFile(fileName)
        
        #-----------------------------------------------------------------------------------------
        # Let's find out if the report arrived on time.  If so, write the report bulletin
        # to disk.
        #-----------------------------------------------------------------------------------------
        self.logger.info("The bulletin timestap is: %s" %self.bulletin.getTimeStamp())
        if (self.isReportOnTime()):
            self.bulletinWriter.writeOnTimeBulletinToDisk(self.bulletin)
        else:
            #-----------------------------------------------------------------------------------------
            # In this section we'll attempt to determine the value of the Collection's B1 anb B2 
            # variables. 
            #-----------------------------------------------------------------------------------------
            if (self.doesReportHaveBbbField()):
                self.bulletin.setCollectionB1(self.bulletin.getReportB1())
                self.bulletin.setCollectionB2(self.bulletin.getReportB2())
            else:
                self.bulletin.setCollectionB1("R")
                self.bulletin.setCollectionB2("R")

            #-----------------------------------------------------------------------------------------
            # In this section we'll attempt to determine the value of the Collection's B3 variable
            #-----------------------------------------------------------------------------------------
            if (self.isReportOlderThan24H()):
                self.bulletin.setCollectionB3("Z")
            else:
                pass
        #-----------------------------------------------------------------------------------------
        # COMPLETEME
        #-----------------------------------------------------------------------------------------
        print "The collection's BBB is now:", self.bulletin.getCollectionBBB()
        return 'COMPLETEME:THIS IS A FAKE RETURN IN CollectionManager.py'


    def isReportOnTime(self):
        """ isReportOnTime() -> Boolean

            Given the bulletin, returns True if the bulletin is considered on time
            and an empty string if the bulletin is not considered on time.

            The incoming bulletin is considered on time if it is from less than
            futureDatedReportWindow mintues in the future and for hourly bulletins only,
            it is less than headerValidTime minutes late.

            Return Values:
                True: string    -Returned if bulletin is considered on time.
                False: string   -Returned if bulletin is not considered on time.
        """
        True = 'True'
        False = ''
        #-----------------------------------------------------------------------------------------
        # Only reports created for the top of the hour may be considered on time.
        #-----------------------------------------------------------------------------------------
        reportPeriodMins = self.bulletin.getBulletinMinutesField()
        if (reportPeriodMins == '00'):
            
            #-----------------------------------------------------------------------------------------
            # Find out how many minutes past the hour is considered on-time for this bulletin type
            #-----------------------------------------------------------------------------------------
            maxPastDateInMins = self.collectionConfig. \
            getReportValidTimeByHeader(self.bulletin.getTwoLetterHeader())

            #-----------------------------------------------------------------------------------------
            # Find out how far in the future an acceptable report may be
            #-----------------------------------------------------------------------------------------
            maxFutureDateInMins = self.collectionConfig. \
            getFutureDatedReportWindowByHeader(self.bulletin.getTwoLetterHeader())

            #-----------------------------------------------------------------------------------------
            # In order for this bulletin to be on time, it must fall in between the maximum past
            # date and the maximum future date
            #-----------------------------------------------------------------------------------------
            futureCheck = self.isBulletinWithinFutureWindow(maxFutureDateInMins)
            pastCheck = self.isBulletinWithinPastWindow(maxPastDateInMins)

            #-----------------------------------------------------------------------------------------
            # If bulletin falls in between both limits, then it is on time
            #-----------------------------------------------------------------------------------------
            if (futureCheck) and (pastCheck):
                return True
            else:
                return False
        else:
            return False

        
    def isBulletinWithinFutureWindow(self, maxFutureDateInMins):
        """ isBulletinWithinFutureWindow(maxFutureDateInMins) -> Boolean

            This method makes sure that the incoming bulletin does not exceed the 
            maximum future date.  It will return a boolean value of True or False
            based on the outcome
        """
        True = 'True'
        False = ''
        #-----------------------------------------------------------------------------------------
        # Produce time objects needed for comparisons.
        # The bulletin has no month or year, so assume present year and month
        #-----------------------------------------------------------------------------------------
        presentDateTime = datetime.datetime.now()
        maxFutureDateTime = presentDateTime + datetime.timedelta(minutes = long(maxFutureDateInMins))
        bulletinDateTime = datetime.datetime(presentDateTime.year, presentDateTime.month, \
                           int(self.bulletin.getBulletinDaysField()), \
                           int(self.bulletin.getBulletinHoursField()), \
                           int(self.bulletin.getBulletinMinutesField())) 

        #-----------------------------------------------------------------------------------------
        # If our maxFutureDateTime spans into a new year, then it is possible
        # that the bulletin may have the new year as its year
        #-----------------------------------------------------------------------------------------
        if (maxFutureDateTime.year > presentDateTime.year):
            bulletinDateTime = bulletinDateTime.replace(year = maxFutureDateTime.year)

        #-----------------------------------------------------------------------------------------
        # If our maxFutureDateTime spans into a new month, then it is possible
        # that the bulletin may have the new month as its month
        #-----------------------------------------------------------------------------------------
        if (maxFutureDateTime.month != presentDateTime.month):
            bulletinDateTime = bulletinDateTime.replace(month = maxFutureDateTime.month)

        #-----------------------------------------------------------------------------------------
        # If the bulletin is still more futuristic than the maxFutureDateTime, then it's from 
        # too far into the future to be considered on time.
        #-----------------------------------------------------------------------------------------
        if (bulletinDateTime > maxFutureDateTime):
            return False
        else:
            return True


    def isBulletinWithinPastWindow(self, maxPastDateInMins):
        """ isBulletinWithinPastWindow(maxPastDateInMins) -> Boolean

            This method accepts a variable in minutes and returns False 
            if the incoming bulletin is older than maxPastDateInMins.  
            It will return True if the bulletin is newer than the 
            maxPastDateInMins.
        """
        True = 'True'
        False = ''
        #-----------------------------------------------------------------------------------------
        # Produce time objects needed for comparisons.
        # The bulletin has no month or year, so assume present year and month
        #-----------------------------------------------------------------------------------------
        presentDateTime = datetime.datetime.now()
        maxPastDateTime = presentDateTime - datetime.timedelta(minutes = long(maxPastDateInMins))
        bulletinDateTime = datetime.datetime(presentDateTime.year, presentDateTime.month, \
                           int(self.bulletin.getBulletinDaysField()), \
                           int(self.bulletin.getBulletinHoursField()), \
                           int(self.bulletin.getBulletinMinutesField())) 

        #-----------------------------------------------------------------------------------------
        # If our maxPastDateTime spans into a previous year, then it is possible
        # that the bulletin may have the previous year as its year
        #-----------------------------------------------------------------------------------------
        if (maxPastDateTime.year < presentDateTime.year):
            bulletinDateTime = bulletinDateTime.replace(year = maxPastDateTime.year)

        #-----------------------------------------------------------------------------------------
        # If our maxPastDateTime spans into a previous month, then it is possible
        # that the bulletin may have the previous month as its month
        #-----------------------------------------------------------------------------------------
        if (maxPastDateTime.month != presentDateTime.month):
            bulletinDateTime = bulletinDateTime.replace(month = maxPastDateTime.month)

        #-----------------------------------------------------------------------------------------
        # If the bulletin is still older than the maxPastDateTime, then it's too old and 
        # cannot be considered on time.
        #-----------------------------------------------------------------------------------------
        if (bulletinDateTime < maxPastDateTime):
            return False
        else:
            return True


    def doesReportHaveBbbField(self):
        """ doesReportHaveBbbField() -> Boolean

            This method makes returns True if the incoming bulletin has a BBB field 
            specified.  It will return False if a BBB field is not specified
        """
        True = 'True'
        False = ''
        #-----------------------------------------------------------------------------------------
        # get the BBB field of the bulletin
        #-----------------------------------------------------------------------------------------
        bulletinBBB = self.bulletin.getReportBBB()

        #-----------------------------------------------------------------------------------------
        # The report has a BBB field if the returning string was not empty
        #-----------------------------------------------------------------------------------------
        if (bulletinBBB):
            return True
        else:
            return False


    def isReportOlderThan24H(self):
        """ isReportOlderThan24H -> Boolean

            This method returns True if the incoming bulletin is older than
            24 hours and False if it is not.
        """
        True = 'True'
        False = ''
        #-----------------------------------------------------------------------------------------
        # 24 hours equals 1440 minutes.  
        # A returned value of true from isBulletinWithinPastWindow means that the 
        # bulletin is not older than 24 hours
        #-----------------------------------------------------------------------------------------
        if (self.isBulletinWithinPastWindow(1440)):
            return False
        else:
            return True





if __name__ == '__main__':
    pass
