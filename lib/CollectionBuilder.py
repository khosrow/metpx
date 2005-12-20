# -*- coding: UTF-8 -*-
"""        
#############################################################################################
# Name: CollectionBuilder.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           Travis Tiegs (National Software Development<nssib@ec.gc.ca>)
#
# Date: 2005-12-19
#
# Description:  This module handles creating Collections from various inputs.
#               You could consider it a way of abstracting collection constructor
#               overloading.
#
# Revision History: 
#               
#############################################################################################
"""
__version__ = '1.0'

import BulletinCollection
from Logger import Logger

class CollectionBuilder:
    """ CollectionBuilder():

        This class is responsible for creating BulletinCollection objects from various.

        This class will add the following attributes to a bulletin:

            b1SubField          string
            b2SubField          string
            b3SubField          string 
                                -Represents the corresponding B in the BBB field for 
                                a report or bulletin

            bulletinTimeStamp   string
                                -Timestamp for this bulletin
            

    """

    def __init__(self,logger):
        self.logger = logger            # Logger object
        self.lineSeparator = '\n'       # Liner separator used when generating bulletin

    def buildBulletinFromFile(self,fileName):
        """ This method loads the information in the given file into a 
            bulletin object and returns it

        """
        #-----------------------------------------------------------------------------------------
        # Open the file and read contents
        #-----------------------------------------------------------------------------------------
        file = open(fileName, 'r')
        rawBulletin = file.read()

        #-----------------------------------------------------------------------------------------
        # Call upon BulletinCollection to produce a bulletin object based on the info
        # read from the file
        #-----------------------------------------------------------------------------------------
        bulletinObject = BulletinCollection.BulletinCollection(rawBulletin, self.logger, self.lineSeparator)
        
        #-----------------------------------------------------------------------------------------
        # Returning a bulletin object based on info in given filename
        #-----------------------------------------------------------------------------------------
        return bulletinObject

