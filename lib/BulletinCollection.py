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

            BBB     string
                    -Represents the BBB field for a report or bulletin

            bulletinTimeStamp   string
                                -Timestamp for this bulletin
            

    """


    def getTimeStamp(self):
        """ getTimeStamp() parses the header and returns the timestamp as a string

        """
        #-----------------------------------------------------------------------------------------
        # split header into tokens
        #-----------------------------------------------------------------------------------------
        headerTokens = string.split(self.getHeader()) 

        #-----------------------------------------------------------------------------------------
        # the timstamp is always the last token in header
        #-----------------------------------------------------------------------------------------
        timeStamp = headerTokens[len(headerTokens) - 1] 

        return timeStamp

        """ REMOVEME: The following single line is equivelent to getTimeStamp():
        return string.split(self.getHeader())[len(string.split(self.getHeader())) -1]
        """


    """ The following get & set methods are here to make CollectionManager easy to read
        They do the obvious.
    """
    def getBBB(self):
        return self.BBB

    def setBBB(newBBB):
        self.BBB = newBBB
            
    def getB1(self):
        return self.BBB[0]

    def getB2(self):
        return self.BBB[1]

    def getB3(self):
        return self.BBB[2]

    def setB1(newB):
        self.BBB[0] = newB

    def setB2(newB):
        self.BBB[1] = newB

    def setB3(newB):
        self.BBB[2] = newB


   
