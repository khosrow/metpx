# -*- coding: UTF-8 -*-
"""        
#############################################################################################
# Name: BulletinCollection.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           Travis Tiegs (National Software Development<nssib@ec.gc.ca>)
#
# Date: 2005-12-19
#
# Description:  This module extends the PX's standard bulletin and gives us the
#               functionality needed for collection operations.
#
# Revision History: 
#               
#############################################################################################
"""
__version__ = '1.0'

import bulletin
import string
from Logger import Logger

class BulletinCollection(bulletin.bulletin):
    """ BulletinCollection(bulletin.bulletin):

        This class extends PX's bulletin class and adds the methods we need
        in order to carry out collections.
        This class will add the following attributes to a bulletin:

            collectionBBB     string
                    -Represents the BBB field for a collection

            bulletinTimeStamp   string
                                -Timestamp for this bulletin
            

    """
    #-----------------------------------------------------------------------------------------
    # Class attributes
    #-----------------------------------------------------------------------------------------
    collectionBBB = '   '

    def getTimeStamp(self):
        """ getTimeStamp() parses the header and returns the timestamp as a string

        """
        #-----------------------------------------------------------------------------------------
        # split header into tokens
        #-----------------------------------------------------------------------------------------
        headerTokens = string.split(self.getHeader()) 

        #-----------------------------------------------------------------------------------------
        # the timstamp is always the third token in header
        #-----------------------------------------------------------------------------------------
        timeStamp = headerTokens[2] 
        return timeStamp

    
    """ The following get & set methods are here to make CollectionManager easy to read
        They do the obvious.
    """
    def getCollectionBBB(self):
        return string.strip(self.collectionBBB)

    def setCollectionBBB(self, newCollectionBBB):
        self.collectionBBB = newCollectionBBB
            
    def getCollectionB1(self):
        return self.collectionBBB[0]

    def getCollectionB2(self):
        return self.collectionBBB[1]

    def getCollectionB3(self):
        return self.collectionBBB[2]

    def setCollectionB1(self, newCollectionB):
        self.collectionBBB = "%s%s%s" % (newCollectionB, self.collectionBBB[1], self.collectionBBB[2])

    def setCollectionB2(self, newCollectionB):
        self.collectionBBB = "%s%s%s" % (self.collectionBBB[0], newCollectionB, self.collectionBBB[2])

    def setCollectionB3(self, newCollectionB):
        self.collectionBBB = "%s%s%s" % (self.collectionBBB[0], self.collectionBBB[1], newCollectionB)

    def getTwoLetterHeader(self):
        """ getTwoLetterHeaderp() parses the header and returns the two letter header
            (I.e 'SA' will be returned for 'SACNXX')
        """
        #-----------------------------------------------------------------------------------------
        # split header into tokens
        #-----------------------------------------------------------------------------------------
        headerTokens = string.split(self.getHeader()) 

        #-----------------------------------------------------------------------------------------
        # the first two letters of the first element make up the two-letter header
        #-----------------------------------------------------------------------------------------
        TwoLetterHeader = headerTokens[0] 
        return TwoLetterHeader[:2]


    def getBulletinMinutesField(self):
        """ getBulletinMinutesField() parses the header and returns the minutes field
            of the bulletin.
        """
        #-----------------------------------------------------------------------------------------
        # get the timestamp
        #-----------------------------------------------------------------------------------------
        timeStamp = self.getTimeStamp() 
        
        #-----------------------------------------------------------------------------------------
        # the minutes field is made up of the last two chars in the timestamp in DDHHMM
        #-----------------------------------------------------------------------------------------
        minutesField = timeStamp[(len(timeStamp) -2):]
        return minutesField


    def getBulletinHoursField(self):
        """ getBulletinHoursField() parses the header and returns the hours field
            of the bulletin.
        """
        #-----------------------------------------------------------------------------------------
        # get the timestamp
        #-----------------------------------------------------------------------------------------
        timeStamp = self.getTimeStamp()  

        #-----------------------------------------------------------------------------------------
        # the hours field is made up of the middle two chars in the timestamp in DDHHMM
        #-----------------------------------------------------------------------------------------
        hoursField = timeStamp[2:4]
        return hoursField


    def getBulletinDaysField(self):
        """ getBulletinDaysField() parses the header and returns the days field
            of the bulletin.
        """
        #-----------------------------------------------------------------------------------------
        # get the timestamp
        #-----------------------------------------------------------------------------------------
        timeStamp = self.getTimeStamp()  

        #-----------------------------------------------------------------------------------------
        # the hours field is made up of the first two chars in the timestamp in DDHHMM
        #-----------------------------------------------------------------------------------------
        daysField = timeStamp[:2]
        return daysField


    def getReportBBB(self):
        """ getReportBBB() -> String || False

            parses the header and returns the BBB field
            in the bulletin, or False if one does not exist.
        """
        False == ''
        #-----------------------------------------------------------------------------------------
        # split header into tokens
        #-----------------------------------------------------------------------------------------
        headerTokens = string.split(self.getHeader()) 
        
        #-----------------------------------------------------------------------------------------
        # The header looks like "SACN58 CWAO 231334 BBB".  The BBB field is the fourth element
        #-----------------------------------------------------------------------------------------
        if (len(headerTokens) > 3):
            return headerTokens[3]
        else:
            return False


    def getReportB1(self):
        """ getReportB1() -> Char || False

            parses the header and returns the first element
            of the BBB field in the bulletin, or False if one 
            does not exist.
        """
        False == ''
        #-----------------------------------------------------------------------------------------
        # get the report's BBB field
        #-----------------------------------------------------------------------------------------
        reportBBB = self.getReportBBB()
        
        #-----------------------------------------------------------------------------------------
        # return first element
        #-----------------------------------------------------------------------------------------
        if (reportBBB):
            return reportBBB[0]
        else:
            return False


    def getReportB2(self):
        """ getReportB2() -> Char || False

            parses the header and returns the second element
            of the BBB field in the bulletin, or False if one 
            does not exist.
        """
        False == ''
        #-----------------------------------------------------------------------------------------
        # get the report's BBB field
        #-----------------------------------------------------------------------------------------
        reportBBB = self.getReportBBB()

        #-----------------------------------------------------------------------------------------
        # return second element
        #-----------------------------------------------------------------------------------------
        if (reportBBB):
            return reportBBB[1]
        else:
            return False


    def bulletinAsString(self):
        """ bulletinAsString([list]) -> string

            Converts a bulletin which is stored as a list into 
            a string.
            (I.e. ['SACN98 CWAO 291600 ','ZMJ SA 1600 AUTO8 M M M 089////M/ 3009 92MM=', '']
                  will be converted into "SACN98 CWAO 291600 
                                          ZMJ SA 1600 AUTO8 M M M 089////M/ 3009 92MM=" 

        """
        #-----------------------------------------------------------------------------------------
        # Stripping out all list related symbols
        #-----------------------------------------------------------------------------------------
        bullString = ''
        for element in self.bulletin:
            bullString = bullString+str(element)+"\n"

        return string.strip(bullString)


    def setReportBBB(self,BBB):
        """ setReportBBB(BBB)

            Given a BBB string, this method sets the report's BBB field to the 
            given BBB variable
        """
        False == ''
        #-----------------------------------------------------------------------------------------
        # split header into tokens
        #-----------------------------------------------------------------------------------------
        headerTokens = string.split(self.getHeader()) 
        
        #-----------------------------------------------------------------------------------------
        # The header looks like "SACN58 CWAO 231334 BBB".  The BBB field is the fourth element
        #-----------------------------------------------------------------------------------------
        if (len(headerTokens) >= 3):
            newHeader = headerTokens[0]+' '+headerTokens[1]+' '+headerTokens[2]+' '+BBB
            self.setHeader(string.strip(newHeader))

        print "REMOVEME: Modified the collection's bbb. New HDR is: ",self.getHeader()
        

    def buildCollectionBulletin(self):
        """ buildCollectionBulletin()

            This method constructs a collection bulletin based on the report
            contained within its bulletin attribute.  The collection bulletin 
            will of course come complete with the the appropriate BBB values.  
            The new collection bulletin is then returned to the caller
        """
        #-----------------------------------------------------------------------------------------
        # Create a collection bulletin which is initially just a copy of the report bulletin
        #-----------------------------------------------------------------------------------------
        newCollectionBulletin = self

        #-----------------------------------------------------------------------------------------
        # Here, we need to update or create the report's BBB value with that of the collection
        #-----------------------------------------------------------------------------------------
        newCollectionBulletin.setReportBBB(newCollectionBulletin.getCollectionBBB())
        return newCollectionBulletin
